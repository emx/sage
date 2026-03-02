import sqlite3
import os
import re
from flask import Flask, render_template, request, g, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/v_forge_cache.db'

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

def waf_filter(val):
    # Hardened filter blocking spaces and common SQLi keywords
    if not val:
        return True
    forbidden = ['union', ' ', '--', '/*', 'or', 'and', 'where', 'sleep']
    for word in forbidden:
        if word in val.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute('SELECT i.*, f.name as facility_name FROM inventory i JOIN facilities f ON i.facility_id = f.id').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/inventory/<int:item_id>')
def item_details(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM inventory WHERE id = ?', (item_id,)).fetchone()
    if item is None:
        abort(404)
    return render_template('item.html', item=item)

@app.route('/facilities')
def facilities():
    db = get_db()
    facilities = db.execute('SELECT * FROM facilities').fetchall()
    return render_template('facilities.html', facilities=facilities)

@app.route('/api/v1/telemetry')
def telemetry_api():
    node_id = request.args.get('node_id', '1')
    sort_by = request.args.get('sort', 'timestamp')

    # Vulnerability: sort_by is directly concatenated into the ORDER BY clause
    # Defense: waf_filter is implemented to make it challenging
    if not waf_filter(sort_by):
        return render_template('error.html', message="Security Violation: Malicious characters detected in query."), 403

    try:
        db = get_db()
        # node_id is parameterized, but sort_by is not.
        query = f"SELECT id, sensor_type, reading, timestamp FROM telemetry_data WHERE node_id = ? ORDER BY {sort_by}"
        data = db.execute(query, (node_id,)).fetchall()
        return render_template('telemetry.html', data=data)
    except Exception as e:
        return render_template('error.html', message="Database Error: Contact System Administrator."), 500

@app.route('/status')
def status():
    return {"status": "online", "nodes": 12, "integrity": "verified"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)