from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
import time
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/verdantpath.db'
API_ACCESS_TOKEN = "v-path-7721-delta-9"

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(payload):
    if not payload:
        return True
    # V-WAF v2.0: Enhanced Security with Case-Insensitive Blacklist and Space-Detection
    # Blacklisting space forces attackers to use alternate whitespace (tabs, newlines)
    # Blacklisting union and comments prevents simple concatenation/termination
    # Blacklisting sleep/benchmark prevents standard time-based exfiltration
    p = payload.lower()
    forbidden = [" ", "union", "sleep", "benchmark", "--", "/*", "#"]
    for word in forbidden:
        if word in p:
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
        if username == 'admin' and password == 'path_finder_2024':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/yields')
def yields():
    db = get_db()
    crops = db.execute('SELECT * FROM crop_yields LIMIT 20').fetchall()
    return render_template('yields.html', crops=crops)

@app.route('/soil')
def soil():
    db = get_db()
    profiles = db.execute('SELECT * FROM soil_profiles').fetchall()
    return render_template('soil.html', profiles=profiles)

@app.route('/telemetry')
def telemetry():
    db = get_db()
    logs = db.execute('SELECT * FROM maintenance_logs').fetchall()
    return render_template('telemetry.html', logs=logs)

@app.route('/api/v1/analytics/export')
def analytics_export():
    # Authentication check: Requires a custom header token discoverable via dashboard source
    token = request.headers.get('X-Access-Token')
    if token != API_ACCESS_TOKEN:
        return jsonify({"error": "Unauthorized: Missing or invalid X-Access-Token header"}), 401

    sort_by = request.args.get('sort_by', 'region')
    
    if not waf_filter(sort_by):
        return jsonify({"error": "Security Alert: Malicious activity detected by V-WAF v2.0"}), 403

    # Introduce a slight delay to discourage heavy automation/brute force
    time.sleep(0.4)

    try:
        db = get_db()
        # Vulnerable ORDER BY injection - restricted by space-less WAF and boolean-blind requirements
        query = f"SELECT region, crop_type, yield_weight FROM crop_yields ORDER BY {sort_by} ASC"
        results = db.execute(query).fetchall()
        data = [dict(row) for row in results]
        return jsonify(data)
    except Exception:
        # Mask internal errors to prevent information leakage
        return jsonify({"error": "Internal Processor Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)