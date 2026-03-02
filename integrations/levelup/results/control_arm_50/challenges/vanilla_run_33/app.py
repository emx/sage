from flask import Flask, render_template, request, jsonify, g
import sqlite3
import os
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Simple WAF to simulate 'Hard' difficulty hurdles
def waf_check(payload):
    blacklist = [r'union', r'or', r'join', r'\-\-', r'truncate', r'drop']
    for pattern in blacklist:
        if re.search(pattern, payload, re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    db = get_db()
    manifests = db.execute("SELECT * FROM shipping_manifests ORDER BY shipping_date DESC LIMIT 10").fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/silos')
def silos():
    db = get_db()
    silos = db.execute("SELECT * FROM grain_inventory").fetchall()
    return render_template('silos.html', silos=silos)

@app.route('/api/v1/silo/<int:silo_id>/stats')
def silo_stats(silo_id):
    period = request.args.get('period', '24 hours')
    
    if not waf_check(period):
        return jsonify({"error": "Malicious activity detected", "status": "blocked"}), 403

    db = get_db()
    # The vulnerability: Unsafe string interpolation into a datetime function call
    # The application expects something like '24 hours' or '7 days'
    query = f"""
        SELECT temperature, recorded_at 
        FROM silo_health_metrics 
        WHERE silo_id = ? 
        AND recorded_at > datetime('now', '-{period}')
        ORDER BY recorded_at ASC
    """
    
    try:
        cursor = db.execute(query, (silo_id,))
        results = cursor.fetchall()
        data = [{"t": r['temperature'], "d": r['recorded_at']} for r in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Database error", "detail": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "operational", "version": "2.4.1-stable"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)