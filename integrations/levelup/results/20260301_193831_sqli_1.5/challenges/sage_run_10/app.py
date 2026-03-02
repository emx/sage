import sqlite3
import os
import re
from flask import Flask, request, render_template, session, redirect, url_for, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/logistics.db'

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

def waf_filter(payload):
    # Hardened WAF: blocks common keywords if they are isolated as words
    # This forces attackers to use non-standard syntax (e.g., SELECT(1) or SELECT\t)
    blacklist = [r'\bSELECT\b', r'\bUNION\b', r'\bOR\b', r'\bAND\b', r'\bWHERE\b', r'--', r'/\*', r'\bSLEEP\b']
    if not payload:
        return True
    for pattern in blacklist:
        if re.search(pattern, payload, re.IGNORECASE):
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
            session['user'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/fleet')
def fleet():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    drivers = db.execute('SELECT * FROM fleet').fetchall()
    return render_template('fleet.html', drivers=drivers)

@app.route('/audit', methods=['GET', 'POST'])
def audit():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    logs = []
    query_filter = request.args.get('filter', '')
    
    # Vulnerable injection point
    if query_filter:
        if not waf_filter(query_filter):
            return render_template('audit.html', error="Security Violation: Malicious patterns detected.", logs=[])
        
        try:
            db = get_db()
            # Direct concatenation into a WHERE clause
            query = f"SELECT id, timestamp, action, details FROM audit_logs WHERE {query_filter}"
            logs = db.execute(query).fetchall()
        except Exception as e:
            # Do not leak the full error for blind SQLi challenge
            return render_template('audit.html', error="Database Error: Query failed.", logs=[])
    else:
        db = get_db()
        logs = db.execute("SELECT id, timestamp, action, details FROM audit_logs LIMIT 10").fetchall()
        
    return render_template('audit.html', logs=logs)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)