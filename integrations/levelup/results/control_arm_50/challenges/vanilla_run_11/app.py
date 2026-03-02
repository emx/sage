import sqlite3
import re
import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/aetherflow.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def check_waf(val):
    # Hardened filter: Blocks spaces, comments, and specific keywords
    blacklist = ['union', 'where', ' ', '--', '/*', 'waitfor', 'delay']
    if not val:
        return True
    for word in blacklist:
        if word in val.lower():
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

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    sort_col = request.args.get('sort', 'flight_num')
    
    # Vulnerability: Blind SQLi in ORDER BY
    if not check_waf(sort_col):
        return abort(403, description="Security Violation Detected: Malicious characters in query.")

    db = get_db()
    try:
        # Unsafe string formatting for ORDER BY
        query = f"SELECT flight_num, cargo_weight, destination, status FROM manifests ORDER BY {sort_col}"
        items = db.execute(query).fetchall()
    except Exception as e:
        # Generic error to prevent easy debugging, but valid for timing/boolean
        return render_template('error.html', message="Sort operation failed.")

    return render_template('manifests.html', items=items)

@app.route('/internal/diagnostics')
def diagnostics():
    # A hidden endpoint that provides hints
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('admin_debug.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message=str(e.description)), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)