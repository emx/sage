import sqlite3
from flask import Flask, render_template, request, redirect, session, g
from config import DATABASE, SECRET_KEY
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(payload):
    # Hardened WAF: Blocks common SQL keywords and spaces
    blacklist = ['SELECT ', 'UNION ', 'WHERE ', 'AND ', 'OR ', 'SLEEP', '--', ' ']
    for word in blacklist:
        if word in payload.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/login')
    db = get_db()
    fields = db.execute('SELECT * FROM field_settings').fetchall()
    return render_template('dashboard.html', fields=fields)

@app.route('/sensors/<int:field_id>')
def sensors(field_id):
    if 'user_id' not in session: return redirect('/login')
    db = get_db()
    field = db.execute('SELECT * FROM field_settings WHERE id = ?', (field_id,)).fetchone()
    if not field: return "Field not found", 404
    
    # VULNERABILITY: Second-order SQLi in ORDER BY
    # The 'sort_pref' comes from the DB and is concatenated directly.
    try:
        query = f"SELECT ph_level, nitrogen, timestamp FROM sensor_logs WHERE field_id = {field_id} ORDER BY {field['sort_pref']}"
        logs = db.execute(query).fetchall()
    except:
        logs = []
    
    return render_template('sensors.html', field=field, logs=logs)

@app.route('/settings/<int:field_id>', methods=['GET', 'POST'])
def settings(field_id):
    if 'user_id' not in session: return redirect('/login')
    db = get_db()
    if request.method == 'POST':
        sort_pref = request.form.get('sort_pref', 'timestamp')
        if not waf_check(sort_pref):
            return "Security Violation: Malicious pattern detected.", 403
        
        db.execute('UPDATE field_settings SET sort_pref = ? WHERE id = ?', (sort_pref, field_id))
        db.commit()
        return redirect(f'/sensors/{field_id}')
    
    field = db.execute('SELECT * FROM field_settings WHERE id = ?', (field_id,)).fetchone()
    return render_template('settings.html', field=field)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/v1/health')
def health():
    return {"status": "online", "version": "2.4.1-stable"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)