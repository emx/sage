import os
import sqlite3
from flask import Flask, render_template, request, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/verdant_axis.db'

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

def security_filter(payload):
    # VerdantAxis 'Aegis-Shield' WAF
    blacklist = ['union', 'or', 'and', '--', '/*', ' ', '\t', '\n', '\r', 'sleep', 'benchmark', 'join']
    if not payload:
        return True
    for word in blacklist:
        if word in payload.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments LIMIT 10').fetchall()
    return render_template('dashboard.html', shipments=shipments)

@app.route('/shipment/<int:shipment_id>')
def shipment_detail(shipment_id):
    db = get_db()
    shipment = db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)).fetchone()
    if not shipment:
        return render_template('error.html', message="Shipment not found"), 404
    telemetry = db.execute('SELECT * FROM telemetry WHERE shipment_id = ? ORDER BY timestamp DESC LIMIT 5', (shipment_id,)).fetchall()
    return render_template('shipment.html', shipment=shipment, telemetry=telemetry)

@app.route('/api/v1/telemetry/archive')
def telemetry_archive():
    shipment_id = request.args.get('shipment_id', '')
    sensor_type = request.args.get('sensor_type', '')

    # Vulnerable endpoint with WAF bypass required
    if not security_filter(sensor_type):
        return jsonify({"status": "error", "message": "Security violation detected by Aegis-Shield WAF"}), 403

    db = get_db()
    try:
        # Unsafe string concatenation for the sensor_type field within a subset of the query
        query = f"SELECT sensor_type, value, timestamp FROM telemetry WHERE shipment_id = ? AND sensor_type = '{sensor_type}'"
        results = db.execute(query, (shipment_id,)).fetchall()
        
        data = [dict(row) for row in results]
        return jsonify({"status": "success", "results": data})
    except Exception as e:
        return jsonify({"status": "error", "message": "Internal Database Error"}), 500

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)