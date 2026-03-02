import sqlite3
import re
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def waf_check(input_str):
    # Hardened WAF: Blocks keywords if they are surrounded by spaces or at word boundaries
    # Also blocks common comment markers and spaces
    blacklist = [r'UNION\s+', r'SELECT\s+', r'WHERE\s+', r'OR\s+', r'AND\s+', r'\s+OR\b', r'\s+AND\b', r'\s+', r'--', r'/\*']
    for pattern in blacklist:
        if re.search(pattern, input_str, re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Standard login (not the intended vulnerability)
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'stratos_vane_2024':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/shipments')
def shipments():
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments').fetchall()
    return render_template('shipments.html', shipments=shipments)

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/v1/telemetry/search', methods=['POST'])
def telemetry_search():
    data = request.get_json()
    if not data or 'tag' not in data:
        return jsonify({'error': 'Missing tag parameter'}), 400

    tag_query = data['tag']
    
    if not waf_check(tag_query):
        return jsonify({'error': 'Security violation detected', 'details': 'Malicious input pattern matched'}), 403

    try:
        db = get_db()
        # Vulnerable Sink: String formatting into query
        query = f"SELECT id, sensor_type, last_ping, status FROM telemetry WHERE tag = '{tag_query}' AND status = 'active'"
        results = db.execute(query).fetchall()
        
        if results:
            return jsonify([dict(row) for row in results])
        else:
            return jsonify({'message': 'No active sensors found for this tag'}), 404
    except Exception as e:
        return jsonify({'error': 'Database error', 'debug': str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)