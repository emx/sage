import sqlite3
import re
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/aetherflow.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(payload):
    # Blacklist common SQL injection keywords
    blacklist = ['UNION', 'SELECT', 'WHERE', 'OR', 'AND', '--', '/*', '*/', 'SLEEP', 'BENCHMARK']
    for word in blacklist:
        if re.search(re.escape(word), payload, re.IGNORECASE):
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
        # Simple authentication for demo purposes
        if username == 'admin' and password == 'AetherFlow2024!':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests LIMIT 5').fetchall()
    return render_template('dashboard.html', manifests=manifests)

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    search = request.args.get('q', '')
    db = get_db()
    # Safe search for manifests
    query = "SELECT * FROM manifests WHERE vessel_name LIKE ? OR container_id LIKE ?"
    results = db.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    return render_template('manifests.html', results=results)

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/v1/telemetry', methods=['POST'])
def telemetry():
    # This internal API is the vulnerability point
    data = request.get_json()
    if not data or 'node_id' not in data or 'sensor_class' not in data:
        return jsonify({"status": "error", "message": "Invalid telemetry format"}), 400

    node_id = str(data.get('node_id'))
    sensor_class = str(data.get('sensor_class'))

    if waf_filter(sensor_class):
        return jsonify({"status": "error", "message": "Security Violation: Malicious patterns detected"}), 403

    try:
        db = get_db()
        # VULNERABLE: Direct string interpolation into the filter clause
        # The query is designed to be blind. It checks if a sensor is registered.
        query = f"SELECT id FROM sensor_registry WHERE node_id = ? AND class = '{sensor_class}'"
        result = db.execute(query, (node_id,)).fetchone()

        if result:
            return jsonify({"status": "success", "data": "Sensor Status: ACTIVE"})
        else:
            return jsonify({"status": "success", "data": "Sensor Status: OFFLINE"})
    except Exception as e:
        # Minimal error leakage
        return jsonify({"status": "error", "message": "Internal processing error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)