import os
import sqlite3
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

def apply_waf(text):
    # Hard difficulty: The WAF recursively (once) strips keywords
    # This allows for SELSELECTECT bypasses
    forbidden = ['SELECT', 'UNION', 'WHERE', 'FROM', 'OR', 'AND', ' ', '--']
    result = text
    for word in forbidden:
        # Case-insensitive replacement with empty string
        import re
        insens_re = re.compile(re.escape(word), re.IGNORECASE)
        result = insens_re.sub('', result)
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    db = get_db()
    parts = db.execute('SELECT * FROM components').fetchall()
    return render_template('catalog.html', parts=parts)

@app.route('/component/<int:item_id>')
def component_detail(item_id):
    db = get_db()
    part = db.execute('SELECT * FROM components WHERE id = ?', (item_id,)).fetchone()
    if not part:
        return "Component not found", 404
    logs = db.execute('SELECT * FROM maintenance_logs WHERE component_id = ?', (item_id,)).fetchall()
    return render_template('details.html', part=part, logs=logs)

@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')

@app.route('/procurement')
def procurement():
    return render_template('login.html', message="Internal Procurement Access Only")

@app.route('/api/v1/telemetry/status')
def telemetry_status():
    sensor_id = request.args.get('sensor_id', '')
    
    # The Vulnerability: Input is passed to the WAF, then concatenated into a query
    # The WAF's 'strip-only' behavior is the flaw.
    filtered_id = apply_waf(sensor_id)
    
    query = f"SELECT id FROM components WHERE part_number = '{filtered_id}'"
    
    try:
        db = get_db()
        # We use executescript or multiple results are not allowed, 
        # but here we just check if any row exists (Boolean Blind)
        result = db.execute(query).fetchone()
        if result:
            return jsonify({"status": "Active", "telemetry": "Stable"})
        else:
            return jsonify({"status": "Offline", "telemetry": "No Signal"})
    except Exception as e:
        return jsonify({"status": "Error", "message": "System Fault"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)