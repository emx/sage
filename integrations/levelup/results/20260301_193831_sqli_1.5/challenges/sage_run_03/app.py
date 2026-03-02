import sqlite3
import os
from flask import Flask, render_template, request, jsonify, g
from config import DATABASE_PATH, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def security_filter(payload):
    # A realistic but flawed WAF
    blacklist = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'JOIN', 'SLEEP', 'benchmark', 'GROUP BY', 'INSERT', 'UPDATE', 'DELETE']
    normalized = payload.upper()
    # Check for keywords with spaces or common delimiters
    for word in blacklist:
        if word in normalized:
            return False
    if " " in payload:
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    silos = db.execute("SELECT * FROM silo_metadata").fetchall()
    return render_template('inventory.html', silos=silos)

@app.route('/shipments')
def shipments():
    db = get_db()
    query = request.args.get('q', '')
    if query:
        results = db.execute("SELECT * FROM shipments WHERE destination LIKE ?", (f'%{query}%',)).fetchall()
    else:
        results = db.execute("SELECT * FROM shipments LIMIT 10").fetchall()
    return render_template('shipments.html', results=results)

@app.route('/tracking')
def tracking():
    return render_template('trace_tool.html')

@app.route('/api/v1/telemetry')
def telemetry_api():
    serial = request.args.get('serial', '')
    if not serial:
        return jsonify({"status": "error", "message": "Missing serial number"}), 400
    
    if not security_filter(serial):
        return jsonify({"status": "error", "message": "Security violation detected"}), 403

    db = get_db()
    try:
        # Vulnerable Sink
        query = f"SELECT id FROM silo_metadata WHERE silo_serial = '{serial}'"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify({"status": "valid", "telemetry": "Active", "last_sync": "2023-10-24 08:42:01"})
        else:
            return jsonify({"status": "invalid", "message": "Serial not found in registry"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Database engine error"}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/health')
def health():
    return jsonify({"status": "online", "version": "2.4.1-stable"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)