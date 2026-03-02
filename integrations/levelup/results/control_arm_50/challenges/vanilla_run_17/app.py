import sqlite3
import os
from flask import Flask, request, render_template, redirect, url_for, session, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(payload):
    # Aetheria Proprietary Threat Detection Layer (WAF)
    blacklist = ['UNION', 'OR', 'AND', '--', '/*', ' ', 'SLEEP', 'BENCHMARK']
    if not payload:
        return True
    for word in blacklist:
        if word in payload.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    shipment = None
    if request.method == 'POST':
        shipment_id = request.form.get('id', '')
        conn = get_db_connection()
        # Safe query using parameters
        shipment = conn.execute('SELECT * FROM manifests WHERE tracking_number = ?', (shipment_id,)).fetchone()
        conn.close()
    return render_template('tracking.html', shipment=shipment)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
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

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    sort_column = request.args.get('sort', 'id')
    
    # Vulnerable logic: Input is checked by WAF but then concatenated
    if not security_filter(sort_column):
        return abort(403, description="Security Violation Detected: Malicious input pattern identified by Aetheria WAF.")

    try:
        conn = get_db_connection()
        # SQL Injection Vulnerability here
        query = f"SELECT * FROM manifests ORDER BY {sort_column}"
        items = conn.execute(query).fetchall()
        conn.close()
        return render_template('manifests.html', items=items)
    except Exception as e:
        return render_template('error.html', message="Database sorting error.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)