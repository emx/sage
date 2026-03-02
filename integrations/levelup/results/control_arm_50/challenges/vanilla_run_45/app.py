import os
import sqlite3
import re
import shutil
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
app.config.from_object('config.Config')

DB_SOURCE = '/tmp/velocis_maritime.db'
DB_PATH = '/tmp/vms_runtime.db'

def get_db_connection():
    # Ensure DB is in writable /tmp
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
        os.chmod(DB_PATH, 0o666)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(data):
    # A realistic but flawed keyword stripping WAF
    keywords = ['SELECT', 'UNION', 'WHERE', 'FROM', 'OR', 'AND', 'LIMIT', 'ORDER', 'BY']
    filtered = data
    for kw in keywords:
        # Case-insensitive replacement of keywords with empty string (non-recursive)
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        filtered = pattern.sub('', filtered)
    
    # Block obvious space usage to force more advanced techniques
    if ' ' in filtered:
        return None
    return filtered

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fleet')
def fleet():
    conn = get_db_connection()
    vessels = conn.execute('SELECT * FROM vessels').fetchall()
    conn.close()
    return render_template('fleet.html', vessels=vessels)

@app.route('/fleet/details/<int:id>')
def vessel_details(id):
    conn = get_db_connection()
    vessel = conn.execute('SELECT * FROM vessels WHERE id = ?', (id,)).fetchone()
    manifests = conn.execute('SELECT * FROM cargo_manifests WHERE vessel_id = ?', (id,)).fetchall()
    conn.close()
    if vessel is None:
        abort(404)
    return render_template('vessel_details.html', vessel=vessel, manifests=manifests)

@app.route('/v-track/portal')
def vtrack_portal():
    return render_template('portal.html')

@app.route('/api/v1/cargo/weight', methods=['GET'])
def get_cargo_weight():
    # Requirement for internal header discovered in JS
    api_key = request.headers.get('X-VTrack-Internal-Key')
    if api_key != 'vtrack-debug-2024':
        return jsonify({"error": "Unauthorized internal access only"}), 401

    cargo_id = request.args.get('id', '')
    if not cargo_id:
        return jsonify({"error": "Missing cargo ID"}), 400

    # Pass through WAF
    cleaned_id = waf_filter(cargo_id)
    if cleaned_id is None:
        return jsonify({"error": "Security Violation: Spaces detected"}), 403

    try:
        conn = get_db_connection()
        # VULNERABILITY: Raw string formatting with stripped input
        query = f"SELECT id, weight, unit, destination FROM cargo_manifests WHERE id = '{cleaned_id}'"
        result = conn.execute(query).fetchone()
        conn.close()

        if result:
            return jsonify({
                "status": "success",
                "id": result['id'],
                "weight": result['weight'],
                "unit": result['unit'],
                "destination": result['destination']
            })
        else:
            return jsonify({"error": "Cargo item not found"}), 404
    except Exception as e:
        return jsonify({"error": "Database error", "debug": str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)