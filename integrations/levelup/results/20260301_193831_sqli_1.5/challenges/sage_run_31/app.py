import os
import sqlite3
import re
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aether_orbital_super_secret_key_9921'
DATABASE = '/tmp/aetherlogix.db'

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

def waf_filter(payload):
    # Simulated WAF blocking common keywords and spaces
    blacklist = ['UNION', 'SELECT', 'WHERE', 'OR', 'AND', 'SLEEP', 'HEX', 'BIN']
    if any(word in payload.upper() for word in blacklist):
        return False
    if ' ' in payload:
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute('SELECT * FROM components LIMIT 10').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/schedules')
def schedules():
    db = get_db()
    launches = db.execute('SELECT * FROM launch_schedules ORDER BY launch_date ASC').fetchall()
    return render_template('schedules.html', launches=launches)

@app.route('/diagnostics')
def diagnostics():
    return render_template('diagnostics.html')

@app.route('/personnel')
def personnel():
    # Security through obscurity: only accessible if you know the route
    db = get_db()
    staff = db.execute('SELECT name, role, location FROM personnel WHERE role != "Admin"').fetchall()
    return render_template('personnel.html', staff=staff)

@app.route('/api/v1/telemetry', methods=['POST'])
def telemetry_api():
    # Legacy API endpoint for internal telemetry lookups
    data = request.get_json()
    if not data or 'sensor_id' not in data:
        return jsonify({"error": "Missing sensor_id"}), 400
    
    sensor_id = str(data['sensor_id'])
    
    if not waf_filter(sensor_id):
        return jsonify({"error": "Security Alert: Malicious input detected"}), 403

    db = get_db()
    try:
        # Vulnerable query: String concatenation with a weak WAF
        query = f"SELECT sensor_name, reading, status FROM telemetry WHERE sensor_id = {sensor_id}"
        result = db.execute(query).fetchone()
        if result:
            return jsonify(dict(result))
        return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', message="Internal Authentication System Offline. Use physical keycard.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)