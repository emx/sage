import sqlite3
import os
import re
import shutil
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "vanguard_meridian_logistics_ultra_secret_2024"
DATABASE = '/tmp/vanguard_logistics.db'
DB_TEMPLATE = '/app/vanguard_logistics.db.bak'

def get_db():
    # Ensure DB exists in /tmp for write access on read-only FS
    if not os.path.exists(DATABASE):
        if os.path.exists(DB_TEMPLATE):
            shutil.copy(DB_TEMPLATE, DATABASE)
        else:
            import init_db
            init_db.initialize()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(text):
    if not text:
        return ""
    # Hardened WAF: Strips dangerous keywords once
    # Vulnerable to: SELSELECTECT -> SELECT
    pattern = re.compile(r'(SELECT|UNION|WHERE|AND|OR|FROM|SLEEP|LIMIT|--|/\*)', re.IGNORECASE)
    return pattern.sub('', str(text))

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
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests LIMIT 10').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/api/v1/docs')
def api_docs():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('docs.html')

@app.route('/api/v1/telemetry/metrics', methods=['POST'])
def telemetry_metrics():
    if 'user_id' not in session: 
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    filter_clause = data.get('filter', '1=1')
    
    # Apply "Security Hardening"
    clean_filter = waf_filter(filter_clause)
    
    try:
        db = get_db()
        # Dangerous direct concatenation
        query = f"SELECT status FROM fleet_telemetry WHERE {clean_filter}"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify({"status": "active", "node": "PRIMARY_VML"})
        else:
            return jsonify({"status": "inactive", "node": "PRIMARY_VML"})
    except Exception as e:
        return jsonify({"status": "error", "message": "System Fault"}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)