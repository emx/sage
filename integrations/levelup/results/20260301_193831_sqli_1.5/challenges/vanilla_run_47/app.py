import sqlite3
import os
import re
import functools
from flask import Flask, render_template, request, jsonify, g, send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
DATABASE = '/tmp/verdant_logistics.db'

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

def security_filter(val):
    """Multi-layer WAF for internal audit endpoint."""
    if not val:
        return True
    # Layer 1: Strict Whitespace Filtering
    if any(char.isspace() for char in val):
        return False
    # Layer 2: Blacklist keywords (forcing more creative SQL syntax like HAVING or CASE)
    blacklist = ['UNION', 'OR', 'AND', 'SLEEP', 'BENCHMARK', 'JOIN', 'LIMIT', '--', '/*']
    # Note: We allow /**/ by specifically checking the blacklist BEFORE the SQL engine sees it,
    # but we've blocked the comment dash --. 
    # However, we must allow the string AX- for legitimate use.
    normalized = val.upper()
    for word in blacklist:
        if word in normalized:
            # Allow '/**/' specifically by checking if it's the only comment style used
            if word == '/*' and '/**/' in normalized:
                continue
            return False
    return True

def require_internal_auth(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Requirement: Discovery of the internal header from static JS assets
        auth_key = request.headers.get('X-Audit-Internal-Key')
        if auth_key != 'd94e3345155f':
            return jsonify({'error': 'Unauthorized: Internal Management Key Missing'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/api/v1/shipment/status', methods=['POST'])
def shipment_status():
    tracking_id = request.json.get('tracking_id', '')
    db = get_db()
    cursor = db.execute('SELECT * FROM shipments WHERE tracking_id = ?', (tracking_id,))
    shipment = cursor.fetchone()
    if shipment:
        return jsonify(dict(shipment))
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/v1/inventory/filter')
def inventory_filter():
    category = request.args.get('category', 'All')
    # Legacy WAF (distraction preserved but hardened)
    if not security_filter(category):
        return jsonify({'error': 'Security violation detected'}), 403
    
    db = get_db()
    query = f"SELECT * FROM inventory WHERE category = '{category}'"
    try:
        cursor = db.execute(query)
        items = [dict(row) for row in cursor.fetchall()]
        return jsonify(items)
    except Exception:
        return jsonify({'error': 'Internal Database Error'}), 500

@app.route('/api/v1/internal/audit')
@require_internal_auth
def internal_audit():
    asset_tag = request.args.get('asset_tag', '')
    
    if not asset_tag.startswith('AX-'):
        return jsonify({'error': 'Invalid asset tag format'}), 400

    # Hardened WAF application
    if not security_filter(asset_tag):
        return jsonify({'error': 'Malicious payload detected'}), 406

    db = get_db()
    # BLIND SQL INJECTION: Removed reflection and changed column count to prevent easy UNION
    # Original query had 3 columns, now it has 4. Vault has 3. 
    query = f"SELECT id, name, location, last_inspected FROM assets WHERE asset_tag = '{asset_tag}'"
    try:
        cursor = db.execute(query)
        result = cursor.fetchone()
        # Return only boolean-style feedback (Blind)
        if result:
            return jsonify({'status': 'success', 'authorized': True})
        else:
            return jsonify({'status': 'success', 'authorized': False})
    except Exception as e:
        # Mask errors to prevent error-based extraction
        return jsonify({'status': 'error', 'msg': 'Audit system processing failure'}), 500

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)