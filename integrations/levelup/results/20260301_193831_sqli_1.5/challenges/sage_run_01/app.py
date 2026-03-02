import sqlite3
import os
from flask import Flask, render_template, request, jsonify, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def check_waf(payload):
    # Hardened WAF blocking common SQLi keywords
    blacklist = ['union', 'or ', 'and ', '--', '/*', 'hex', 'sleep', 'benchmark', 'join']
    if not payload:
        return True
    payload_lower = payload.lower()
    for word in blacklist:
        if word in payload_lower:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM inventory_items LIMIT 20').fetchall()
    conn.close()
    return render_template('inventory.html', items=items)

@app.route('/inventory/view/<int:item_id>')
def view_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM inventory_items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    if item is None:
        abort(404)
    return render_template('details.html', item=item)

@app.route('/status')
def status():
    conn = get_db_connection()
    facilities = conn.execute('SELECT * FROM facilities').fetchall()
    conn.close()
    return render_template('status.html', facilities=facilities)

@app.route('/api/v1/telemetry')
def telemetry_api():
    facility_id = request.args.get('facility_id', '1')
    sort_col = request.args.get('sort', 'timestamp')

    if not check_waf(sort_col):
        return jsonify({"error": "Security Alert: Malicious pattern detected by Veridian WAF"}), 403

    try:
        conn = get_db_connection()
        # Vulnerable ORDER BY injection point
        query = f"SELECT timestamp, reading, sensor_type FROM climate_logs WHERE facility_id = ? ORDER BY {sort_col}"
        logs = conn.execute(query, (facility_id,)).fetchall()
        conn.close()
        return jsonify([dict(row) for row in logs])
    except Exception as e:
        # Errors are bubbled up, which helps in error-based SQLi
        return jsonify({"error": str(e)}), 500

@app.route('/about')
def about():
    return render_template('base.html', content="Veridian Gilt Logistics has been the industry leader in high-value asset relocation since 1984.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Red herring login
    if request.method == 'POST':
        return render_template('login.html', error="Invalid credentials. Portal access is restricted to verified coordinators.")
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)