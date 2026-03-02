import sqlite3
import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "aetheria_super_secret_key_882211"
DB_PATH = '/tmp/aetheria_telematics.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(s):
    if not s:
        return "timestamp"
    # Hardened WAF: Removes dangerous keywords and whitespace
    keywords = ['SELECT', 'UNION', 'WHERE', 'FROM', 'AND', 'OR', 'LIMIT', 'OFFSET', '--', '/*']
    filtered = s
    for kw in keywords:
        # Non-recursive replacement (vulnerability point)
        filtered = re.sub(re.escape(kw), '', filtered, flags=re.IGNORECASE)
    
    if re.search(r'\s', filtered):
        return "timestamp"  # Block all whitespace
    
    return filtered

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/drones')
def drones():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    drones = conn.execute('SELECT * FROM drones').fetchall()
    conn.close()
    return render_template('drones.html', drones=drones)

@app.route('/logs')
def logs():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    sort_val = request.args.get('sort', 'timestamp')
    safe_sort = security_filter(sort_val)
    
    conn = get_db_connection()
    try:
        # Dangerous sorting implementation
        query = f"SELECT * FROM maintenance_logs ORDER BY {safe_sort} ASC"
        logs = conn.execute(query).fetchall()
    except Exception as e:
        # flash(f"Database Error: {str(e)}") # Helpful for debugging, removed for difficulty
        logs = conn.execute("SELECT * FROM maintenance_logs ORDER BY timestamp DESC").fetchall()
    conn.close()
    
    return render_template('logs.html', logs=logs, current_sort=sort_val)

@app.route('/api/v1/hardware/config')
def hardware_config():
    # Undocumented endpoint for hardware specs
    if 'username' not in session:
        return {"error": "Unauthorized"}, 401
    return {
        "system_id": "AE-99-X1",
        "firmware_version": "4.5.12-LTS",
        "last_audit": "2024-10-12",
        "audit_table_ref": "internal_system_data"
    }

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)