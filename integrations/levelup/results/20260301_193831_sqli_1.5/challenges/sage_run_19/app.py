import os
import sqlite3
from flask import Flask, render_template, request, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
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
    blacklist = ['UNION', 'OR', 'AND', '--', '/*', '*/', 'SLEEP', 'BENCHMARK', 'HEX']
    upper_input = input_str.upper()
    for word in blacklist:
        if word in upper_input:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', error="Authentication service is currently undergoing maintenance.")

@app.route('/dashboard')
def dashboard():
    db = get_db()
    drones = db.execute('SELECT * FROM drones LIMIT 5').fetchall()
    return render_template('dashboard.html', drones=drones)

@app.route('/flights')
def flights():
    db = get_db()
    logs = db.execute('SELECT * FROM flight_logs ORDER BY start_time DESC LIMIT 10').fetchall()
    return render_template('flights.html', logs=logs)

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/pilots')
def pilots():
    db = get_db()
    pilots = db.execute('SELECT * FROM pilots').fetchall()
    return render_template('pilots.html', pilots=pilots)

@app.route('/api/v1/logistics/maintenance')
def maintenance_api():
    sort_val = request.args.get('sort', 'date')
    
    if not waf_check(sort_val):
        return jsonify({"error": "Security violation detected. Your IP has been logged."}), 403

    db = get_db()
    try:
        # Vulnerable order-by injection point
        query = f"SELECT id, drone_id, description, date, cost FROM maintenance_records ORDER BY {sort_val} ASC"
        cursor = db.execute(query)
        records = [dict(row) for row in cursor.fetchall()]
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": "Database error occurred during sorting operation."}), 500

@app.route('/maintenance')
def maintenance_page():
    return render_template('maintenance.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)