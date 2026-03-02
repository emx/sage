import sqlite3
import os
from flask import Flask, render_template, request, jsonify, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(payload):
    # Custom WAF: Blocks common SQLi keywords and whitespace techniques
    blacklist = ['UNION', '--', '/*', ' ', 'OR', 'AND']
    if not payload:
        return True
    for item in blacklist:
        if item in payload.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/shipments')
def shipments():
    conn = get_db_connection()
    shipments = conn.execute('SELECT * FROM shipments LIMIT 10').fetchall()
    conn.close()
    return render_template('shipments.html', shipments=shipments)

@app.route('/api/v1/telemetry')
def telemetry_api():
    sort_by = request.args.get('sort', 'timestamp')
    
    if not security_filter(sort_by):
        return abort(403, description="Security Violation: Malicious Pattern Detected")

    conn = get_db_connection()
    try:
        # Intentionally vulnerable to ORDER BY injection
        query = f"SELECT id, sensor_id, reading, timestamp FROM telemetry ORDER BY {sort_by} LIMIT 50"
        logs = conn.execute(query).fetchall()
        conn.close()
        return jsonify([dict(row) for row in logs])
    except Exception as e:
        conn.close()
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)