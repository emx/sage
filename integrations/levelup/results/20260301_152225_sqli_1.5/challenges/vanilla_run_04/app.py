import os
import sqlite3
import re
import shutil
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "v3rd4nt_p7ls3_53cr3t_k3y_2024"
DB_PATH = "/tmp/grain_sentinel.db"
ORIG_DB = "/app/grain_sentinel.db"

# Ensure DB exists in /tmp for read-only FS compliance
if not os.path.exists(DB_PATH):
    shutil.copy(ORIG_DB, DB_PATH)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    # Simulate a realistic WAF that blocks common SQL keywords and spaces
    blacklist = [r"union", r"select", r"where", r"or", r"and", r"sleep", r"--", r"/\*"]
    for pattern in blacklist:
        if re.search(pattern, payload.lower()) and " " in payload:
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM staff_members WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    silos = db.execute('SELECT * FROM silos').fetchall()
    return render_template('dashboard.html', silos=silos)

@app.route('/api/v1/telemetry/logs', methods=['POST'])
def telemetry_api():
    # Hidden API found via JS analysis
    auth_token = request.headers.get('X-Manager-Token')
    if auth_token != 'VP-SECURE-2024-MGMT':
        return jsonify({"status": "error", "message": "Unauthorized Access"}), 403

    data = request.get_json()
    sort_col = data.get('sort', 'id')

    # The Vulnerability: Order By Injection
    # The WAF check is weak: it only triggers if keywords AND spaces are present
    if waf_filter(sort_col):
        return jsonify({"status": "error", "message": "Security Violation Detected"}), 400

    try:
        db = get_db()
        # Dangerous string concatenation
        query = f"SELECT id, location, crop_type, capacity FROM silos ORDER BY {sort_col}"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"status": "error", "message": "Database Error"}), 500

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('inventory.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['user'])

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)