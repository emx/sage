import os
import sqlite3
import re
from flask import Flask, render_template, request, jsonify, g
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

def waf_filter(data):
    # Simple WAF blocking common keywords and spaces in specific contexts
    if not data:
        return False
    forbidden = [' ', 'OR', 'AND', 'SLEEP', 'BENCHMARK']
    for word in forbidden:
        if word in data.upper():
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vessels')
def vessels():
    db = get_db()
    vessels = db.execute('SELECT * FROM vessels').fetchall()
    return render_template('vessels.html', vessels=vessels)

@app.route('/containers')
def containers():
    db = get_db()
    containers = db.execute('SELECT * FROM containers LIMIT 20').fetchall()
    return render_template('containers.html', containers=containers)

@app.route('/manifests')
def manifests():
    return render_template('manifests.html')

@app.route('/api/v1/docs')
def api_docs():
    return jsonify({
        "version": "v1.2.4-stable",
        "endpoints": {
            "/api/v1/vessel/details": {
                "method": "GET",
                "params": ["id"],
                "headers": ["X-Audit-ID"],
                "description": "Internal audit tracking for vessel lookups."
            }
        }
    })

@app.route('/api/v1/vessel/details')
def vessel_details():
    vessel_id = request.args.get('id', '')
    audit_id = request.headers.get('X-Audit-ID', '1')

    # Security check on query params, but header is overlooked for space filtering
    if waf_filter(vessel_id):
        return jsonify({"error": "Malicious input detected in parameters"}), 403
    
    # The vulnerability: audit_id is injected into a secondary lookup
    # and spaces are filtered, but comments /**/ can bypass it.
    if ' ' in audit_id:
        return jsonify({"error": "Spaces not allowed in Audit ID"}), 400

    db = get_db()
    try:
        # Unsafe query construction using the audit_id header
        query = f"SELECT id, name, owner, registry FROM vessels WHERE id = '{audit_id}' OR id = ?"
        vessel = db.execute(query, (vessel_id,)).fetchone()
        
        if vessel:
            return jsonify({
                "id": vessel['id'],
                "name": vessel['name'],
                "owner": vessel['owner'],
                "registry": vessel['registry']
            })
        return jsonify({"error": "Vessel not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "debug": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', error="Authentication service is currently offline for maintenance.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)