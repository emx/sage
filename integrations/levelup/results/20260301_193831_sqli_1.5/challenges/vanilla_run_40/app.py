import os
import sqlite3
import shutil
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'st0_strat0s_l0gix_2024_p3rcisi0n'
DB_PATH = '/tmp/inventory.db'
DB_TEMPLATE = '/app/inventory.db'

# Ensure DB exists in /tmp for read-only FS compliance
if not os.path.exists(DB_PATH):
    shutil.copy(DB_TEMPLATE, DB_PATH)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# WAF: Simple filter that removes dangerous keywords once
def waf_filter(data):
    if not data:
        return data
    keywords = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'FROM', 'SLEEP', '--', '/*']
    for kw in keywords:
        # Case-insensitive replacement
        import re
        data = re.compile(re.escape(kw), re.IGNORECASE).sub('', data)
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute('SELECT * FROM inventory_items').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/locations')
def locations():
    db = get_db()
    warehouses = db.execute('SELECT * FROM warehouses').fetchall()
    return render_template('locations.html', warehouses=warehouses)

@app.route('/manifests')
def manifests():
    db = get_db()
    shipments = db.execute('SELECT * FROM manifests').fetchall()
    return render_template('manifests.html', shipments=shipments)

@app.route('/api/v1/telemetry')
def telemetry():
    node_id = request.args.get('node_id', '1')
    sort_col = request.args.get('sort', 'id')
    
    # Apply WAF
    filtered_sort = waf_filter(sort_col)
    
    try:
        db = get_db()
        # Vulnerable order by injection
        query = f"SELECT id, sensor_type, last_reading, status FROM telemetry_data WHERE node_id = ? ORDER BY {filtered_sort}"
        results = db.execute(query, (node_id,)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database operation failed", "debug": str(e)}), 400

@app.route('/api/v1/status')
def status():
    return jsonify({"system": "StratosLogix Core", "status": "Operational", "version": "4.2.1-stable"})

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)