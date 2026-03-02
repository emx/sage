import sqlite3
import os
import json
import shutil
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
app.config.from_object('config.Config')

DB_PATH = '/tmp/velosync.db'
ORIGINAL_DB = '/app/velosync.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(ORIGINAL_DB, DB_PATH)
        os.chmod(DB_PATH, 0o666)
    
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# WAF: Inspects raw request data before JSON parsing
def security_filter():
    raw_data = request.get_data().decode().upper()
    blacklist = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'JOIN', 'FROM', '--', '/*']
    for word in blacklist:
        if word in raw_data:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', error="The login system is currently under maintenance. Please use dispatcher credentials.")

@app.route('/dashboard')
def dashboard():
    db = get_db()
    stats = {
        'active_vessels': db.execute("SELECT COUNT(*) FROM manifests WHERE status='In Transit'").fetchone()[0],
        'fleet_count': db.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0],
        'system_health': 'Optimal'
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/fleet')
def fleet():
    return render_template('fleet.html')

@app.route('/vessels')
def vessels():
    db = get_db()
    manifests = db.execute("SELECT * FROM manifests LIMIT 10").fetchall()
    return render_template('vessels.html', manifests=manifests)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/v1/inventory', methods=['POST'])
def inventory_api():
    if not security_filter():
        return jsonify({"error": "Security Violation: Malicious SQL detected in request body"}), 403

    try:
        data = request.get_json()
        filter_clause = data.get('filter', '1=1')
        
        db = get_db()
        # The vulnerability: filter_clause is directly concatenated into the query
        query = f"SELECT id, name, type, status FROM vehicles WHERE {filter_clause}"
        results = db.execute(query).fetchall()
        
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Internal System Error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)