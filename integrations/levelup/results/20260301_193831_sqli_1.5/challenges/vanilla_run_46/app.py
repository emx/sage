import sqlite3
import os
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
app.config['SECRET_KEY'] = '592e3d36b76174a72d73318991a0c83a'
DATABASE = '/tmp/aetherflow.db'

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

def waf_filter(val):
    # Simple but annoying WAF
    blacklist = ['UNION', 'OR', 'AND', '--', '/*', 'SLEEP', 'BENCHMARK']
    for word in blacklist:
        if word in val.upper():
            return False
    return True

@app.after_request
def add_header(response):
    response.headers['X-Aether-Service'] = 'Logistics-Web-v2.1'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute('SELECT * FROM inventory LIMIT 20').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/drones')
def drones():
    db = get_db()
    drones = db.execute('SELECT * FROM drones').fetchall()
    return render_template('drones.html', drones=drones)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Rabbit hole: secure login
    return render_template('login.html', error="External authentication is currently disabled.")

@app.route('/internal/analytics')
def analytics():
    if request.headers.get('X-Aether-Internal') != 'true':
        return "Access Denied: Internal Traffic Only", 403
    return render_template('analytics.html')

@app.route('/api/v1/telemetry', methods=['POST'])
def telemetry_api():
    if request.headers.get('X-Aether-Internal') != 'true':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    sort_field = data.get('sort', 'drone_id')
    direction = data.get('direction', 'asc')
    
    if not waf_filter(sort_field):
        return jsonify({"error": "Security Violation Detected"}), 400

    if direction.lower() not in ['asc', 'desc']:
        direction = 'asc'

    db = get_db()
    try:
        # VULNERABILITY: Injection in ORDER BY
        query = f"SELECT drone_id, status, battery_level, last_ping FROM drone_telemetry ORDER BY {sort_field} {direction}"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/status')
def status():
    return jsonify({"status": "online", "version": "2.1.0-stable"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)