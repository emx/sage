import sqlite3
import os
import shutil
import re
from flask import Flask, request, render_template, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_SOURCE = '/app/voyant.db'
DB_PATH = '/tmp/voyant.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def security_filter(payload):
    # A realistic but flawed WAF: it looks for keywords followed by spaces
    # Players can bypass this by using comments (/**/) or other whitespace
    forbidden = ['SELECT ', 'UNION ', 'WHERE ', 'FROM ', 'INSERT ', 'UPDATE ', 'DELETE ', 'DROP ']
    if not payload:
        return True
    for word in forbidden:
        if word.upper() in payload.upper():
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
        if username == 'guest' and password == 'guest':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cur = db.execute('SELECT * FROM manifests LIMIT 20')
    rows = cur.fetchall()
    return render_template('manifests.html', manifests=rows)

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    debug_mode = request.args.get('debug', 'false').lower() == 'true'
    filter_query = request.args.get('filter', '')
    
    db = get_db()
    base_query = "SELECT id, item_name, quantity FROM inventory"
    
    if debug_mode and filter_query:
        if not security_filter(filter_query):
            return "Security Alert: Malicious pattern detected in filter!", 403
        
        # VULNERABILITY: Direct string concatenation in a 'debug' feature
        try:
            full_query = f"{base_query} WHERE {filter_query}"
            cur = db.execute(full_query)
            rows = cur.fetchall()
        except Exception as e:
            return f"Database Error: {str(e)}", 500
    else:
        cur = db.execute(base_query)
        rows = cur.fetchall()
        
    return render_template('inventory.html', items=rows, debug=debug_mode)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)