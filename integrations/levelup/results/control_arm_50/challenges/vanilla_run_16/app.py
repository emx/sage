import sqlite3
import os
from flask import Flask, render_template, request, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/verdant.db'

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

def waf_check(input_str):
    if not input_str:
        return True
    blacklist = ['UNION', 'SELECT', 'OR', 'AND', ' ', '--', 'SLEEP', 'BENCHMARK']
    for word in blacklist:
        if word in input_str.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    parcels = db.execute('SELECT * FROM parcels').fetchall()
    return render_template('dashboard.html', parcels=parcels)

@app.route('/parcel/<int:parcel_id>')
def parcel_detail(parcel_id):
    db = get_db()
    parcel = db.execute('SELECT * FROM parcels WHERE id = ?', (parcel_id,)).fetchone()
    if not parcel:
        return "Parcel not found", 404
    samples = db.execute('SELECT * FROM soil_samples WHERE parcel_id = ? ORDER BY recorded_at DESC LIMIT 5', (parcel_id,)).fetchall()
    return render_template('parcel_detail.html', parcel=parcel, samples=samples)

@app.route('/api/v1/reports')
def api_reports():
    parcel_id = request.args.get('parcel_id', 1)
    sort_by = request.args.get('sort', 'recorded_at')

    if not waf_check(sort_by):
        return jsonify({"error": "Security Violation Detected", "reason": "V-WAF Blocked Malicious Pattern"}), 403

    db = get_db()
    # Vulnerable ORDER BY injection
    try:
        query = f"SELECT nitrogen, phosphorus, ph_level, recorded_at FROM soil_samples WHERE parcel_id = ? ORDER BY {sort_by}"
        cursor = db.execute(query, (parcel_id,))
        results = [dict(row) for row in cursor.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": "Internal Query Error"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "Authentication Service Unavailable", 503
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)