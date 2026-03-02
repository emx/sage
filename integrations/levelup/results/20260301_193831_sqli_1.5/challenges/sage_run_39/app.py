import sqlite3
import os
from flask import Flask, request, render_template, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(32)
DB_PATH = '/tmp/aetheron.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    blacklisted = ["UNION", "OR", "AND", "--", "/*", "SLEEP", "BENCHMARK"]
    for word in blacklisted:
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
        # Simple demo auth
        if username == 'engineer' and password == 'aetheron2024':
            session['user'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    components = db.execute('SELECT * FROM components').fetchall()
    return render_template('inventory.html', components=components)

@app.route('/telemetry')
def telemetry():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    logs = db.execute('SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 10').fetchall()
    return render_template('telemetry.html', logs=logs)

@app.route('/api/v1/health')
def health():
    return jsonify({"status": "online", "systems": "nominal"})

@app.route('/api/v1/telemetry/sync')
def sync_sensor():
    legacy = request.args.get('legacy')
    if legacy != 'true':
        return jsonify({"error": "Standard sync currently unavailable. Use legacy endpoint."}), 400
    
    sensor_id = request.headers.get('X-Legacy-Sensor-ID')
    if not sensor_id:
        return jsonify({"error": "Missing X-Legacy-Sensor-ID header"}), 400

    if not waf_check(sensor_id):
        return jsonify({"error": "Security alert: Illegal characters detected in header"}), 403

    try:
        db = get_db()
        # Vulnerable query: String concatenation with header value
        query = f"SELECT id, model FROM components WHERE id = {sensor_id}"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify({"status": "success", "msg": f"Sensor {result['model']} synchronized"})
        else:
            return jsonify({"status": "error", "msg": "Sensor ID not found"})
    except Exception as e:
        return jsonify({"status": "error", "msg": "Internal Database Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)