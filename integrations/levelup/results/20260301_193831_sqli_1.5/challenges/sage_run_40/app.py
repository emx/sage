import sqlite3
import os
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_PATH = '/tmp/aetherbound.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    # Hardened WAF: Blocking UNION, common comments, and SPACES
    blacklist = ['UNION', '--', '/*', 'OR ', 'AND ', 'SLEEP', 'BENCHMARK', ' ', 'OFFSET']
    if not payload:
        return True
    for item in blacklist:
        if item in payload.upper():
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests LIMIT 5').fetchall()
    return render_template('dashboard.html', manifests=manifests)

@app.route('/tracking')
def tracking():
    tracking_id = request.args.get('id', '')
    manifest = None
    if tracking_id:
        db = get_db()
        manifest = db.execute('SELECT * FROM manifests WHERE tracking_id = ?', (tracking_id,)).fetchone()
    return render_template('tracking.html', manifest=manifest)

@app.route('/api/v1/reports')
def reports_api():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    sort_by = request.args.get('sort', 'id')
    
    if not waf_check(sort_by):
        return jsonify({"error": "Security Alert: Malicious characters detected"}), 403

    try:
        db = get_db()
        # Vulnerable ORDER BY injection point
        query = f"SELECT id, tracking_id, payload_name, weight FROM manifests ORDER BY {sort_by}"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Internal Query Error"}), 500

@app.route('/api/v1/health')
def health():
    return jsonify({"status": "online", "nodes": ["ORD-01", "LHR-02", "HKG-01"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)