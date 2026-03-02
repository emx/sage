import sqlite3
from flask import Flask, render_template, request, jsonify, g
import os
import json
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/thalassa.db'

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

# Custom WAF: Only checks query parameters (GET)
def waf_check():
    blacklist = ['union', 'select', 'where', 'sleep', 'benchmark', 'char', 'hex', '--', '/*']
    for param in request.args.values():
        for word in blacklist:
            if word in param.lower():
                return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', error="Login is currently disabled for external auditors.")

@app.route('/vessels')
def vessels():
    db = get_db()
    vessels = db.execute('SELECT * FROM vessels').fetchall()
    return render_template('vessels.html', vessels=vessels)

@app.route('/vessels/view/<int:vessel_id>')
def vessel_detail(vessel_id):
    db = get_db()
    vessel = db.execute('SELECT * FROM vessels WHERE id = ?', (vessel_id,)).fetchone()
    manifests = db.execute('SELECT * FROM manifests WHERE vessel_id = ?', (vessel_id,)).fetchall()
    return render_template('vessel_detail.html', vessel=vessel, manifests=manifests)

@app.route('/manifests')
def manifests():
    db = get_db()
    manifests = db.execute('SELECT m.*, v.name as vessel_name FROM manifests m JOIN vessels v ON m.vessel_id = v.id LIMIT 50').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/api/v1/reports/vessel', methods=['GET', 'POST'])
def vessel_report():
    if waf_check():
        return jsonify({"status": "error", "message": "Security Violation: SQL Injection Detected"}), 403

    db = get_db()
    vessel_id = None
    sort_field = 'name'

    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        vessel_id = data.get('vessel_id')
        sort_field = data.get('sort', 'name')
    else:
        vessel_id = request.args.get('vessel_id')
        sort_field = request.args.get('sort', 'name')

    if not vessel_id:
        return jsonify({"status": "error", "message": "Missing vessel_id"}), 400

    try:
        # VULNERABILITY: sort_field is directly concatenated into the ORDER BY clause
        query = f"SELECT id, name, registration, status FROM vessels WHERE id = ? ORDER BY {sort_field}"
        results = db.execute(query, (vessel_id,)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"status": "error", "message": "Database error occurred"}), 500

@app.route('/search')
def search():
    q = request.args.get('q', '')
    return render_template('search.html', q=q)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)