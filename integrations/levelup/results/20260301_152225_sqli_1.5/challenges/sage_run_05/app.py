import os
import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, session, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def security_filter(payload):
    # A realistic but flawed WAF filter
    # Blocks keywords if they are followed by spaces or used in common patterns
    blacklist = [r'UNION\s+SELECT', r'OR\s+1=1', r'-- ', r'DROP\s+TABLE', r'INSERT\s+INTO']
    for pattern in blacklist:
        if re.search(pattern, payload, re.IGNORECASE):
            return False
    # Strict check: No spaces allowed in certain contexts to prevent simple bypasses
    if ' ' in payload and ('SELECT' in payload.upper() or 'UNION' in payload.upper()):
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
        # Simple auth for the logistics portal
        if username == 'guest' and password == 'guest123':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute("SELECT * FROM inventory").fetchall()
    return render_template('inventory.html', items=items)

@app.route('/shipments')
def shipments():
    db = get_db()
    logs = db.execute("SELECT * FROM shipments").fetchall()
    return render_template('shipments.html', logs=logs)

@app.route('/audit')
def audit():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    sort_param = request.args.get('sort', 'timestamp')
    
    # The Vulnerability: Order By injection
    # The WAF is active but can be bypassed using SQL comments or specific syntax
    if not security_filter(sort_param):
        return "Security Alert: Malicious activity detected.", 403

    db = get_db()
    try:
        # Unsafe interpolation in ORDER BY clause
        query = f"SELECT id, timestamp, action, details FROM audit_logs ORDER BY {sort_param} DESC"
        logs = db.execute(query).fetchall()
    except Exception as e:
        return f"Database Error: {str(e)}", 500
        
    return render_template('audit.html', logs=logs, current_sort=sort_param)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)