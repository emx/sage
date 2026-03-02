import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DB_PATH = '/tmp/verdant_pulse.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(payload):
    # A realistic but flawed WAF
    blacklist = ['SELECT', 'UNION', 'WHERE', 'OR', 'AND', '--', '/*', ' ']
    if not payload:
        return True
    upper_payload = payload.upper()
    for word in blacklist:
        if word in upper_payload:
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
        # Simple mock login for functionality
        if username and password:
            session['user'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/harvests')
def harvests():
    conn = get_db_connection()
    harvests = conn.execute('SELECT * FROM harvest_logs LIMIT 10').fetchall()
    conn.close()
    return render_template('harvests.html', harvests=harvests)

@app.route('/nutrients')
def nutrients():
    conn = get_db_connection()
    profiles = conn.execute('SELECT * FROM nutrient_profiles').fetchall()
    conn.close()
    return render_template('nutrients.html', profiles=profiles)

@app.route('/api/v1/status')
def status():
    return jsonify({"status": "operational", "nodes": 124, "uptime": "45d 12h"})

@app.route('/api/v1/telemetry/query', methods=['POST'])
def query_telemetry():
    # Internal API discovered via comments
    data = request.get_json()
    if not data or 'sensor_id' not in data:
        return jsonify({"error": "Missing sensor_id parameter"}), 400
    
    sensor_id = str(data['sensor_id'])
    
    if not security_filter(sensor_id):
        return jsonify({"error": "Security Filter Triggered", "reason": "Illegal characters detected"}), 403

    try:
        conn = get_db_connection()
        # Vulnerable query construction
        query = f"SELECT * FROM sensor_telemetry WHERE sensor_id = '{sensor_id}'"
        result = conn.execute(query).fetchone()
        conn.close()
        
        if result:
            return jsonify({"status": "success", "data": dict(result)})
        else:
            return jsonify({"status": "no_data", "message": "No records found for this sensor ID"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": "Database error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)