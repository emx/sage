from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    # Strict WAF blocking common SQLi patterns
    blacklist = ['union', 'or', 'and', 'sleep', 'benchmark', '--', '/*', '*/', 'window', 'delay']
    if any(word in payload.lower() for word in blacklist):
        return False
    # Block actual space characters - forces use of %09 or other whitespace
    if ' ' in payload:
        return False
    return True

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    
    if user:
        session['user'] = user['username']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Invalid credentials")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('index'))
    db = get_db()
    items = db.execute('SELECT * FROM manifests LIMIT 10').fetchall()
    return render_template('manifests.html', items=items)

@app.route('/telemetry')
def telemetry():
    if 'user' not in session:
        return redirect(url_for('index'))
    db = get_db()
    drones = db.execute('SELECT * FROM drones').fetchall()
    return render_template('telemetry.html', drones=drones)

@app.route('/api/v1/telemetry/search')
def telemetry_search():
    if 'user' not in session:
        return abort(401)
    
    sort_by = request.args.get('sort', 'timestamp')
    drone_id = request.args.get('drone_id', '1')

    if not waf_filter(sort_by):
        return jsonify({"error": "Security violation detected", "code": "WAF-403"}), 403

    try:
        db = get_db()
        # Vulnerable order by injection point
        query = f"SELECT * FROM telemetry_logs WHERE drone_id = ? ORDER BY {sort_by}"
        logs = db.execute(query, (drone_id,)).fetchall()
        return jsonify([dict(log) for log in logs])
    except Exception as e:
        return jsonify({"error": "Database error", "detail": str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)