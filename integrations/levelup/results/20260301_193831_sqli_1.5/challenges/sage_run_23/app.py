import os
import sqlite3
import re
from flask import Flask, render_template, request, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = os.urandom(32)
DATABASE = "/tmp/aetherlink.db"

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

def waf_filter(text):
    # A realistic but flawed WAF: single-pass keyword removal
    keywords = ['SELECT', 'UNION', 'FROM', 'WHERE', 'LIKE', 'AND', 'OR', 'LIMIT', 'JOIN', 'SLEEP']
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub('', text)
    return text

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
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/telemetry')
def telemetry():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT display_filter FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Vulnerable second-order injection point
    query = f"SELECT id, satellite_id, sensor_data, timestamp FROM telemetry_logs WHERE satellite_id = 'HORIZON-1' AND ({user['display_filter']})"
    
    try:
        results = db.execute(query).fetchall()
        status = "Nominal" if results else "No Data Recovered"
    except:
        results = []
        status = "System Error: Check Filter Syntax"
        
    return render_template('telemetry.html', logs=results, status=status)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        new_filter = request.form.get('filter', '1=1')
        # Apply WAF
        clean_filter = waf_filter(new_filter)
        db.execute('UPDATE users SET display_filter = ? WHERE id = ?', (clean_filter, session['user_id']))
        db.commit()
        return redirect(url_for('profile', msg="Settings Updated"))
    
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/fleet')
def fleet():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('fleet.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)