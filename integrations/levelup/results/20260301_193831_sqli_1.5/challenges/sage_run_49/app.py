import sqlite3
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    forbidden = ['UNION', 'OR', 'AND', '--', '/*', '*/', 'SLEEP', 'BENCHMARK']
    if not payload:
        return True
    for word in forbidden:
        if word in payload.upper():
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
        # Secure login implementation
        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
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
    db = get_db_connection()
    manifests = db.execute('SELECT * FROM freight_manifests LIMIT 20').fetchall()
    db.close()
    return render_template('manifests.html', manifests=manifests)

@app.route('/telemetry')
def telemetry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    telemetry = db.execute('SELECT * FROM vehicle_telemetry ORDER BY timestamp DESC LIMIT 15').fetchall()
    db.close()
    return render_template('telemetry.html', telemetry=telemetry)

@app.route('/api/v1/network_status')
def network_status():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    sort_param = request.args.get('sort', 'id')
    
    if not waf_filter(sort_param):
        return jsonify({"error": "Security filter triggered"}), 400

    try:
        db = get_db_connection()
        # VULNERABILITY: sort_param is directly concatenated into the ORDER BY clause
        query = f"SELECT id, node_name, status, last_ping FROM network_nodes ORDER BY {sort_param}"
        nodes = db.execute(query).fetchall()
        db.close()
        return jsonify([dict(node) for node in nodes])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)