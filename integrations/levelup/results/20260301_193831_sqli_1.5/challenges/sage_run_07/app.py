import sqlite3
import re
from flask import Flask, render_template, request, jsonify, g
import os

app = Flask(__name__)
app.config['DATABASE'] = '/tmp/velocita_logistics.db'
app.config['SECRET_KEY'] = os.urandom(24)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def security_filter(payload):
    # Middleware that scrubs common SQL keywords to 'prevent' injection
    # Vulnerability: It's not recursive, allowing nested bypasses (e.g., SELSELECTECT)
    keywords = ['SELECT', 'UNION', 'FROM', 'WHERE', 'OR', 'AND', '--', 'LIMIT', 'OFFSET', 'GROUP', 'BY']
    filtered = payload
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        filtered = pattern.sub('', filtered)
    return filtered

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shipments')
def shipments_page():
    return render_template('shipments.html')

@app.route('/api/v1/shipments')
def api_shipments():
    db = get_db()
    sort_column = request.args.get('sort', 'id')
    
    # Apply the 'security' filter
    clean_sort = security_filter(sort_column)
    
    # Dangerous string formatting into the ORDER BY clause
    query = f"SELECT id, tracking_id, origin, destination, status, weight FROM shipments ORDER BY {clean_sort} ASC"
    
    try:
        cursor = db.execute(query)
        shipments = [dict(row) for row in cursor.fetchall()]
        return jsonify(shipments)
    except Exception as e:
        return jsonify({"error": "Database error occurred during sorting operation."}), 400

@app.route('/docs')
def documentation():
    return render_template('docs.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Red herring login page
    if request.method == 'POST':
        return "Login failed: Administrative access restricted to local network nodes only.", 403
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)