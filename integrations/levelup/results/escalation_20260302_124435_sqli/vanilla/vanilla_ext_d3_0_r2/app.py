import sqlite3
import re
import urllib.parse
import hashlib
import time
from flask import Flask, request, jsonify, render_template, g, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Multi-Layer WAF ---
@app.before_request
def waf():
    # Block obvious SQL logic and extraction functions
    for key, values in request.args.lists():
        for val in values:
            decoded = urllib.parse.unquote(val)
            folded = decoded.casefold()
            
            # Blacklist optimized to block implicit comparisons and common extraction techniques
            # We block >, <, = to force use of BETWEEN, and block most string manip functions
            blacklist = [
                'union', 'sleep', 'benchmark', '--', '/*', '#', 
                'hex', 'base64', 'case', 'when', 'then', 'else', 'end', 
                'substr', 'substring', 'mid', 'like', 'glob', 'instr', 
                'char', 'unicode', 'load_extension', 'join', 'group',
                'max', 'min', 'limit', 'offset', 'printf', 'trim', 'replace',
                '>', '<', '=', '"', "'"
            ]
            
            if any(word in folded for word in blacklist):
                return jsonify({"error": "Security Filter Triggered", "reason": "Policy violation"}), 403

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    components = db.execute('SELECT * FROM propulsion_units WHERE category = \'propulsion\' ORDER BY id ASC LIMIT 10').fetchall()
    mode = db.execute('SELECT value FROM system_settings WHERE key = "mode"').fetchone()['value']
    return render_template('dashboard.html', components=components, mode=mode)

@app.route('/api/v1/system/mode', methods=['POST'])
def set_mode():
    # Multi-step requirement: Enable diagnostic mode with a time-locked token
    license_key = "AETHERIS-LIC-9921-X"
    ts = int(time.time() // 60) # Token changes every minute
    expected_token = hashlib.sha256(f"{license_key}{ts}".encode()).hexdigest()
    
    provided_token = request.headers.get('X-System-Token')
    if provided_token != expected_token:
        return jsonify({"error": "Unauthorized", "message": "Invalid or expired system token"}), 401

    data = request.get_json()
    if not data or 'mode' not in data:
        return jsonify({"error": "Invalid specification"}), 400
    
    db = get_db()
    db.execute('UPDATE system_settings SET value = ? WHERE key = "mode"', (data['mode'],))
    db.commit()
    return jsonify({"status": "Operational mode updated", "new_mode": data['mode']})

@app.route('/api/v1/manifest/view/<int:log_id>')
def view_manifest(log_id):
    db = get_db()
    log = db.execute('SELECT * FROM shipping_logs WHERE id = ?', (log_id,)).fetchone()
    if not log:
        abort(404)
    return render_template('manifest.html', log=log)

@app.route('/api/v1/telemetry/data', methods=['GET'])
def telemetry_api():
    # Requirement 1: Static License Key
    license_key = request.headers.get('X-Aetheris-License')
    if not license_key or license_key != "AETHERIS-LIC-9921-X":
        return jsonify({"error": "Forbidden", "message": "Missing License Header"}), 403

    # Requirement 2: Dynamic Nonce-based Signature
    nonce = request.headers.get('X-Aetheris-Nonce', '')
    if len(nonce) < 16:
         return jsonify({"error": "Forbidden", "message": "Invalid Nonce"}), 403
    
    signature = request.headers.get('X-Aetheris-Signature')
    salt = "OBSCURA_SALT_7712"
    expected_sig = hashlib.sha256((license_key + salt + nonce).encode()).hexdigest()
    if signature != expected_sig:
        return jsonify({"error": "Unauthorized", "message": "Invalid Signature"}), 401

    # Requirement 3: Diagnostic State
    db = get_db()
    mode = db.execute('SELECT value FROM system_settings WHERE key = "mode"').fetchone()['value']
    if mode != 'DIAGNOSTIC':
        return jsonify({"error": "System restricted", "message": "Diagnostic Mode Required"}), 403

    # Anti-Bruteforce Rate Limiting (Hardening)
    time.sleep(1.0)

    category = request.args.get('type', 'propulsion')
    sort_order = request.args.get('order', 'id')

    # Requirement 4: Payload Length Hardening
    if len(sort_order) > 65:
        return jsonify({"error": "Payload too long", "message": "Signature limit exceeded"}), 400

    try:
        # Vulnerability: Blind ORDER BY injection
        # Oracle: If expression results in 1, list is sorted by ID (1,2,3,4,5). 
        # If 0, list remains in insertion order (5,4,3,2,1).
        query = f"SELECT id, part_name, status FROM propulsion_units WHERE category = ? ORDER BY {sort_order} ASC LIMIT 5"
        results = db.execute(query, (category,)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)