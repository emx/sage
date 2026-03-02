import sqlite3
import os
from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/velostream.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf(payload):
    if not payload:
        return True
    blacklist = ['UNION', 'OR', 'AND', '--', '/*', ';', 'SLEEP', 'BENCHMARK', 'HEX']
    for word in blacklist:
        if word in payload.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    search = request.args.get('q', '')
    db = get_db()
    if search:
        query = "SELECT * FROM manifests WHERE tracking_id LIKE ? OR destination LIKE ?"
        rows = db.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    else:
        rows = db.execute("SELECT * FROM manifests LIMIT 20").fetchall()
    return render_template('manifests.html', manifests=rows)

@app.route('/drivers')
def drivers():
    db = get_db()
    rows = db.execute("SELECT * FROM drivers").fetchall()
    return render_template('drivers.html', drivers=rows)

@app.route('/reports/internal')
def internal_reports():
    access_tier = request.cookies.get('access_tier')
    if access_tier != 'admin':
        return "Access Denied: Tier level 'admin' required for executive reports.", 403
    
    sort_column = request.args.get('sort', 'id')
    
    if not waf(sort_column):
        return "Security Alert: Malicious characters detected in query parameters.", 400

    db = get_db()
    # Vulnerable ORDER BY injection point
    try:
        query = f"SELECT id, route_id, load_weight, fuel_efficiency, arrival_est FROM logistics_metrics ORDER BY {sort_column} ASC"
        rows = db.execute(query).fetchall()
    except Exception as e:
        return render_template('reports.html', error=str(e), metrics=[])
        
    return render_template('reports.html', metrics=rows)

@app.route('/api/v1/status')
def status_api():
    return jsonify({"status": "operational", "version": "2.4.1", "db_connected": True})

@app.route('/maintenance')
def maintenance():
    db = get_db()
    logs = db.execute("SELECT * FROM maintenance_logs ORDER BY date DESC LIMIT 10").fetchall()
    return render_template('maintenance.html', logs=logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)