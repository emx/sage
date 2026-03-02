import os
import sqlite3
import re
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    if not payload:
        return False
    # Blacklist common SQL keywords followed by spaces or comments
    # The flaw: it doesn't account for keywords followed by parentheses or other delimiters
    forbidden = [
        r"SELECT\s+", r"UNION\s+", r"WHERE\s+", r"OR\s+", r"AND\s+", 
        r"--", r"/\*", r"INSERT\s+", r"UPDATE\s+", r"DELETE\s+", r"DROP\s+"
    ]
    for pattern in forbidden:
        if re.search(pattern, payload, re.IGNORECASE):
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
        if username == 'guest' and password == 'guest':
            session['user'] = 'guest'
            session['role'] = 'viewer'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/fleet')
def fleet():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('fleet.html')

@app.route('/reports')
def reports():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/api/v1/telemetry/history')
def telemetry_history():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    vid = request.args.get('vehicle_id', 'VS-101')
    sort = request.args.get('sort', 'timestamp')

    if waf_filter(sort):
        return jsonify({"error": "Security Alert: Malicious input detected"}), 403

    try:
        conn = get_db_connection()
        # Vulnerable ORDER BY injection
        query = f"SELECT id, vehicle_id, driver, location, cargo, timestamp FROM fleet_logs WHERE vehicle_id = ? ORDER BY {sort}"
        logs = conn.execute(query, (vid,)).fetchall()
        conn.close()
        return jsonify([dict(row) for row in logs])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, message="Resource not found"), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)