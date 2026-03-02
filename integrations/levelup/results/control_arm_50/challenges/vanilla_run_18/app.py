import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    blacklist = ['union', 'sleep', 'benchmark', 'update', 'delete', 'drop', '--', '/*']
    if any(word in payload.lower() for word in blacklist):
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
        if username == 'guest' and password == 'guest123':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/archive')
def archive():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('archive.html')

@app.route('/api/v1/archive/telemetry', methods=['POST'])
def api_telemetry():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    sort_field = data.get('sort', 'id')
    order = data.get('order', 'ASC')

    if not waf_check(sort_field) or not waf_check(order):
        return jsonify({"error": "Malicious activity detected"}), 403

    # Vulnerable ORDER BY injection
    query = f"SELECT id, crop_type, yield_tons, region, moisture_pct FROM harvest_records ORDER BY {sort_field} {order}"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        results = cursor.execute(query).fetchall()
        conn.close()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/system/status')
def status():
    return render_template('status.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)