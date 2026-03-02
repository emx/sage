import sqlite3
from flask import Flask, render_template, request, jsonify, g
import os
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/verdant.db'

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

def waf_filter(input_str):
    # Hardened filter blocking common SQLi keywords and comments
    blacklist = ['UNION', 'OR', '--', '/*', 'SLEEP', 'BENCHMARK', 'OFFSET', 'LIMIT']
    if any(word in input_str.upper() for word in blacklist):
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifests')
def manifests():
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/manifest/<int:id>')
def manifest_detail(id):
    db = get_db()
    manifest = db.execute('SELECT * FROM manifests WHERE id = ?', (id,)).fetchone()
    return render_template('manifest_detail.html', manifest=manifest)

@app.route('/fleet')
def fleet():
    db = get_db()
    vessels = db.execute('SELECT * FROM vessels').fetchall()
    return render_template('fleet.html', vessels=vessels)

@app.route('/fleet/<int:id>')
def vessel_detail(id):
    db = get_db()
    vessel = db.execute('SELECT * FROM vessels WHERE id = ?', (id,)).fetchone()
    return render_template('vessel_detail.html', vessel=vessel)

@app.route('/telemetry/<int:id>')
def telemetry_view(id):
    return render_template('telemetry.html', vessel_id=id)

@app.route('/api/v1/telemetry/<int:id>')
def api_telemetry(id):
    sort_by = request.args.get('sort', 'timestamp')
    
    if not waf_filter(sort_by):
        return jsonify({"error": "Security violation detected"}), 403

    db = get_db()
    try:
        # Vulnerable ORDER BY injection
        query = f"SELECT timestamp, temp_c, humidity FROM telemetry_logs WHERE vessel_id = {id} ORDER BY {sort_by} ASC"
        logs = db.execute(query).fetchall()
        return jsonify([dict(row) for row in logs])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)