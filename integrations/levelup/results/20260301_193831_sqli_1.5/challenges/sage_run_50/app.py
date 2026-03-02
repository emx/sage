import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import DATABASE, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(input_str):
    # Hardened WAF: Blocks spaces, common comment sequences, and union-based keywords
    blacklist = [' ', '--', ';', 'union', 'sleep', 'load_extension', 'hex']
    for item in blacklist:
        if item in input_str.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simple login for simulation
        session['user'] = request.form.get('username')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    satellites = conn.execute('SELECT * FROM satellites').fetchall()
    conn.close()
    return render_template('dashboard.html', satellites=satellites)

@app.route('/satellite/<int:sat_id>')
def satellite_detail(sat_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    satellite = conn.execute('SELECT * FROM satellites WHERE id = ?', (sat_id,)).fetchone()
    conn.close()
    if not satellite:
        return "Satellite not found", 404
    return render_template('satellite.html', satellite=satellite)

@app.route('/telemetry')
def telemetry():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    satellites = conn.execute('SELECT id, name FROM satellites').fetchall()
    conn.close()
    return render_template('telemetry.html', satellites=satellites)

@app.route('/maintenance')
def maintenance():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('maintenance.html')

@app.route('/api/v1/telemetry/query', methods=['POST'])
def api_telemetry_query():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    sat_id = data.get('satellite_id')
    sort_field = data.get('sort', 'timestamp')

    if not waf_check(str(sort_field)):
        return jsonify({"error": "Security Violation: Malformed Sort Parameter Detected"}), 403

    try:
        conn = get_db_connection()
        # Vulnerable: sort_field is concatenated directly into the ORDER BY clause
        query = f"SELECT sensor_type, value, timestamp FROM telemetry_logs WHERE satellite_id = ? ORDER BY {sort_field}"
        results = conn.execute(query, (sat_id,)).fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)