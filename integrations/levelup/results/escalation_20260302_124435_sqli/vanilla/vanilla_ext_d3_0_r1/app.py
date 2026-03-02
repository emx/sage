import sqlite3
import os
import re
from flask import Flask, request, jsonify, render_template, g

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
DATABASE = '/tmp/vanguard.db'

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

def waf_check(payload):
    # Enhanced WAF for restricted maintenance tunnel
    # All common SQL keywords and delimiters are scrutinized
    blacklist = [
        "SELECT", "UNION", "WHERE", "LIMIT", "OFFSET", "OR", "AND", 
        "LIKE", "AS", "GROUP", "HAVING", "ORDER", "GLOB", "MATCH", 
        "--", "/*", "'", "\"", " "
    ]
    if not payload:
        return True
    
    payload_upper = payload.upper()
    for item in blacklist:
        if item in payload_upper:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    stats = db.execute("SELECT status, COUNT(*) as count FROM satellites GROUP BY status").fetchall()
    return render_template('dashboard.html', stats=stats)

@app.route('/satellites')
def satellites():
    db = get_db()
    sats = db.execute("SELECT * FROM satellites").fetchall()
    return render_template('satellites.html', satellites=sats)

@app.route('/telemetry/<int:sat_id>')
def telemetry(sat_id):
    db = get_db()
    sat = db.execute("SELECT * FROM satellites WHERE id = ?", (sat_id,)).fetchone()
    logs = db.execute("SELECT * FROM telemetry_logs WHERE satellite_id = ? ORDER BY timestamp DESC LIMIT 10", (sat_id,)).fetchall()
    return render_template('telemetry.html', sat=sat, logs=logs)

@app.route('/api/health')
def health():
    return jsonify({"status": "operational", "subsystems": "all-green"})

@app.route('/api/telemetry/maintenance/archive', methods=['POST'])
def archive_query():
    # Internal Maintenance Tunnel
    if request.headers.get('X-Vanguard-Debug') != '1':
        return jsonify({"status": "error", "message": "Access denied. Maintenance tunnel restricted."}), 403

    data = request.get_json()
    if not data or 'mode' not in data or 'source' not in data:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    mode = data.get('mode')
    source = data.get('source')

    if mode == 'legacy':
        if not waf_check(source):
            return jsonify({"status": "error", "message": "Security Violation: Blocked character or keyword detected"}), 400
        
        try:
            db = get_db()
            # Legacy wrapper for specialized telemetry calculations
            query = f"SELECT COUNT(*) FROM ({source}) WHERE 1=1"
            result = db.execute(query).fetchone()
            return jsonify({"status": "success", "count": result[0]})
        except Exception:
            return jsonify({"status": "error", "message": "Query execution failure"}), 500
    
    return jsonify({"status": "error", "message": "Unsupported mode"}), 400

@app.route('/docs')
def docs():
    return render_template('docs.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)