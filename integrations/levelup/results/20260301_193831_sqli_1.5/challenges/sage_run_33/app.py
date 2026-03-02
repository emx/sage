import sqlite3
import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db_path = '/tmp/veridian.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    # Simulated WAF blocking common keywords and spaces
    blacklist = ['UNION', 'SELECT', 'FROM', 'WHERE', ' ']
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
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search = request.args.get('q', '')
    db = get_db()
    query = "SELECT * FROM manifests WHERE manifest_id LIKE ? OR destination LIKE ?"
    results = db.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    return render_template('manifests.html', manifests=results)

@app.route('/fleet')
def fleet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    ships = db.execute('SELECT * FROM fleet_assets').fetchall()
    return render_template('fleet.html', ships=ships)

@app.route('/api/v1/logistics/telemetry')
def telemetry_api():
    # Vulnerable Legacy Endpoint
    unit_id = request.args.get('unit_id', '')
    
    if not unit_id:
        return jsonify({"error": "Missing unit_id"}), 400

    if not waf_check(unit_id):
        return jsonify({"error": "Security Violation: Malformed request detected"}), 403

    db = get_db()
    try:
        # Intentionally vulnerable to SQL injection
        query = f"SELECT status FROM telemetry_units WHERE unit_id = '{unit_id}'"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify({"status": "active", "data": result['status']})
        else:
            return jsonify({"status": "inactive", "data": None}), 404
    except Exception as e:
        return jsonify({"error": "Database operation failed"}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)