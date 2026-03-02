import sqlite3
import re
from flask import Flask, render_template, request, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE_PATH'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_filter(payload):
    # Mimic a restrictive WAF that blocks spaces, comments, and specific keywords
    blacklist = [' ', '--', '/*', 'union', 'or ', 'and ', 'sleep', 'benchmark', 'join']
    for item in blacklist:
        if item in payload.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/shipments')
def shipments():
    return render_template('shipments.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    items = db.execute("SELECT * FROM inventory").fetchall()
    return render_template('inventory.html', items=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/v1/shipments/query')
def query_shipments():
    sort_by = request.args.get('sort', 'id')
    
    if not waf_filter(sort_by):
        return jsonify({"status": "error", "message": "Security Alert: Malicious pattern detected in sort parameter."}), 403

    try:
        db = get_db()
        # Vulnerable ORDER BY injection
        query = f"SELECT id, tracking_no, origin, destination, status FROM shipments ORDER BY {sort_by}"
        results = db.execute(query).fetchall()
        
        shipment_list = []
        for row in results:
            shipment_list.append(dict(row))
            
        return jsonify(shipment_list)
    except Exception as e:
        return jsonify({"status": "error", "message": "Database error occurred during processing."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)