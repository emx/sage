import sqlite3
import os
import re
from flask import Flask, render_template, request, session, redirect, url_for, g, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/orbitstream.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(input_str):
    # A realistic but flawed WAF regex
    # Blocks common keywords but can be bypassed with comments or case variance depending on implementation
    keywords = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'JOIN', 'LIMIT', 'SLEEP']
    for kw in keywords:
        if re.search(rf'\b{kw}\b', input_str, re.IGNORECASE):
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
        # Standard login logic (simulated)
        if username == 'admin' and password == 'orbit_cargo_2024':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    search = request.args.get('q', '')
    db = get_db()
    query = "SELECT * FROM manifests"
    params = []
    if search:
        query += " WHERE cargo_id LIKE ? OR destination LIKE ?"
        params = [f"%{search}%", f"%{search}%"]
    
    rows = db.execute(query, params).fetchall()
    return render_template('manifests.html', manifests=rows)

@app.route('/api/v1/telemetry/report')
def telemetry_report():
    # Internal API endpoint for legacy device tracking
    device_id = request.args.get('device_id', 'DEV-001')
    sort_by = request.args.get('sort', 'timestamp')

    # Vulnerability: sort_by is directly concatenated into the ORDER BY clause
    # WAF is applied to mitigate risk
    if waf_check(sort_by):
        return abort(403, description="Security Violation: Forbidden Keywords Detected")

    db = get_db()
    try:
        # The vulnerability is here: string concatenation in ORDER BY
        query = f"SELECT id, device_id, timestamp, status FROM access_logs WHERE device_id = ? ORDER BY {sort_by} DESC"
        rows = db.execute(query, (device_id,)).fetchall()
        
        results = [dict(row) for row in rows]
        return render_template('telemetry.html', results=results)
    except Exception as e:
        return render_template('telemetry.html', error=str(e))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)