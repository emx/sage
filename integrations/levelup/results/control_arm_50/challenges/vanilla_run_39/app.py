import sqlite3
import os
from flask import Flask, render_template, request, g, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Database is in /tmp for read-only FS compatibility
        db = g._database = sqlite3.connect(Config.DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def verdant_shield_filter(payload):
    """Proprietary security filter to prevent SQL Injection."""
    if not payload:
        return True
    
    blacklist = [
        'UNION', 'OR', 'AND', 'SLEEP', 'BENCHMARK', 
        '--', '/*', '*/', 'HEX', 'BASE64', 'LOAD_FILE'
    ]
    
    normalized_payload = str(payload).upper()
    for word in blacklist:
        if word in normalized_payload:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    crops = db.execute("SELECT * FROM silo_inventory").fetchall()
    return render_template('inventory.html', crops=crops)

@app.route('/silo/<silo_id>')
def silo_detail(silo_id):
    # Security Check
    if not verdant_shield_filter(silo_id):
        return render_template('error.html', message="Security violation detected by VerdantShield!"), 403

    db = get_db()
    try:
        # Vulnerable query: string concatenation
        query = f"SELECT * FROM silo_inventory WHERE silo_id = {silo_id}"
        silo = db.execute(query).fetchone()
    except Exception as e:
        return render_template('error.html', message="Database Error", debug=str(e)), 500

    if silo:
        return render_template('dashboard.html', silo=silo)
    else:
        abort(404)

@app.route('/chemical-logs')
def chemical_logs():
    db = get_db()
    logs = db.execute("SELECT * FROM chemical_applications LIMIT 10").fetchall()
    return render_template('logs.html', logs=logs)

@app.route('/status')
def status():
    return render_template('status.html', system_status="Operational", nodes=24)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Resource not found"), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)