import os
import sqlite3
import shutil
from flask import Flask, render_template, request, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database exists in /tmp/ for read-write access if needed,
# although we only perform reads. Required for read-only FS compliance.
DB_PATH = '/tmp/velonexus.db'
if not os.path.exists(DB_PATH):
    shutil.copy('/app/velonexus.db', DB_PATH)

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

def waf_check(payload):
    if not payload:
        return True
    # Hardened WAF: blocks spaces and standard SQL keywords
    blacklist = [' ', 'UNION', 'OR', 'AND', '--', '/*', '*/']
    p_upper = payload.upper()
    for term in blacklist:
        if term in p_upper:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shipments')
def shipments():
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments LIMIT 20').fetchall()
    return render_template('shipments.html', shipments=shipments)

@app.route('/shipment/<int:shipment_id>')
def shipment_detail(shipment_id):
    db = get_db()
    shipment = db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)).fetchone()
    if not shipment:
        return "Shipment not found", 404
    return render_template('details.html', shipment=shipment)

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

@app.route('/docs/api')
def api_docs():
    return render_template('api_docs.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', error="Staff authentication is currently restricted to local terminal access.")

@app.route('/api/v1/shipments')
def api_shipments():
    sort_col = request.args.get('sort', 'id')
    # Requirement: X-FMS-Debug header must be 1 for advanced sorting
    is_debug = request.headers.get('X-FMS-Debug') == '1'
    
    if not is_debug and sort_col != 'id':
        return jsonify({"error": "Advanced sorting requires internal debug privileges"}), 403

    if not waf_check(sort_col):
        return jsonify({"error": "Security Blocked: Malicious pattern detected in sort parameter"}), 400

    try:
        db = get_db()
        # Vulnerable ORDER BY injection
        query = f"SELECT id, container_id, origin, destination, status FROM shipments ORDER BY {sort_col} LIMIT 50"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error", "detail": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)