import sqlite3
import os
import re
import time
from flask import Flask, render_template, request, jsonify, g
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

# Hardened WAF: Replaced simple space-check with regex and strict character filtering
def waf_check(input_str):
    if not input_str:
        return True

    # 1. Block UNION and OR using word boundaries to prevent trivial bypasses
    # This forces the attacker to use Boolean-based exfiltration instead of UNION
    forbidden_keywords = ["UNION", "OR", "SLEEP", "BENCHMARK", "GROUP BY"]
    for word in forbidden_keywords:
        if re.search(rf"\b{word}\b", input_str, re.IGNORECASE):
            return False

    # 2. Block common SQL comment sequences
    if any(x in input_str for x in ["--", "#", "/*"]):
        return False

    # 3. Block literal spaces and tabs (Flask decodes %20 and %09 to these)
    # To bypass this, attackers must use alternative whitespace like Newlines (%0a), 
    # Form Feeds (%0c), or Carriage Returns (%0d).
    if " " in input_str or "\t" in input_str:
        return False

    return True

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    db = get_db()
    query = "SELECT * FROM manifests LIMIT 10"
    manifests = db.execute(query).fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/fleet')
def fleet():
    db = get_db()
    fleet = db.execute("SELECT * FROM fleet").fetchall()
    return render_template('fleet.html', fleet=fleet)

@app.route('/api/v1/telemetry')
def telemetry_api():
    # Requirement 1: Hidden Header authentication to reach the telemetry logic
    auth_header = request.headers.get('X-Device-Auth')
    if auth_header != "aetheris-api-v12-telemetry":
        return jsonify({"error": "Unauthorized Access: Legacy protocol header missing"}), 401

    device_id = request.args.get('device_id', '')
    
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    if not waf_check(device_id):
        return jsonify({"error": "Security Alert: Malicious activity detected"}), 403

    # Hardening: Simulated processing delay to slow down automated exfiltration
    time.sleep(0.05)

    db = get_db()
    try:
        # Vulnerable injection point (unquoted integer)
        query = f"SELECT id, name, status FROM fleet WHERE id = {device_id}"
        result = db.execute(query).fetchone()
        
        # Hardening: Blind SQLi. No longer returns database content in the response.
        # Only returns status (online/offline), forcing boolean-based extraction.
        if result:
            return jsonify({
                "status": "online", 
                "timestamp": int(time.time()),
                "node": f"AETHERIS-TX-{str(result['id']).zfill(3)}"
            })
        else:
            return jsonify({"status": "offline", "timestamp": int(time.time()), "node": None})
    except Exception as e:
        # Masking database errors to prevent error-based SQLi
        return jsonify({"error": "System Communication Error"}), 500

@app.route('/api/v1/search_manifests')
def search_manifests():
    q = request.args.get('q', '')
    db = get_db()
    results = db.execute("SELECT * FROM manifests WHERE destination LIKE ?", ('%' + q + '%',)).fetchall()
    return jsonify([dict(r) for r in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)