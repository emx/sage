import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/vortex.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    if not payload:
        return True
    # Realistic WAF: blocks common keywords and symbols
    blacklist = [' ', '--', '/*', 'UNION', 'OR', 'AND', 'WHERE', 'SLEEP']
    upper_payload = payload.upper()
    for item in blacklist:
        if item in upper_payload:
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
        
        # Secure authentication for login
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    sort_column = request.args.get('sort', 'id')
    
    # Vulnerability: Unsafe string concatenation in ORDER BY
    # The WAF blocks spaces and common keywords, forcing a specific bypass
    if not waf_check(sort_column):
        return render_template('error.html', message="Security Alert: Malicious pattern detected in query."), 403

    db = get_db()
    try:
        query = f"SELECT id, container_id, origin, destination, weight, status FROM shipments ORDER BY {sort_column} ASC"
        shipments = db.execute(query).fetchall()
    except Exception as e:
        return render_template('error.html', message="Database error occurred during report generation."), 500

    return render_template('reports.html', shipments=shipments, current_sort=sort_column)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="The requested resource was not found."), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)