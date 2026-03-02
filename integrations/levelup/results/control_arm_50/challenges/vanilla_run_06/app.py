import sqlite3
import os
import re
from flask import Flask, request, render_template, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

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

def security_filter(text):
    # A naive filter that attempts to prevent SQLi by stripping keywords
    # Vulnerable to recursive bypass: SELSELECTECT -> SELECT
    keywords = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'LIMIT', 'OFFSET', 'SLEEP', 'FROM']
    filtered = text
    for word in keywords:
        regex = re.compile(re.escape(word), re.IGNORECASE)
        filtered = regex.sub('', filtered)
    return filtered

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/silos')
def silos():
    db = get_db()
    silos = db.execute('SELECT * FROM silos').fetchall()
    return render_template('silos.html', silos=silos)

@app.route('/shipments')
def shipments():
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments').fetchall()
    return render_template('shipments.html', shipments=shipments)

@app.route('/inspections', methods=['GET', 'POST'])
def inspections():
    db = get_db()
    query = ""
    results = []
    if request.method == 'POST':
        query = request.form.get('inspector_id', '')
        # Securely parameterized query here as a red herring
        results = db.execute('SELECT * FROM inspections WHERE inspector_id = ?', (query,)).fetchall()
    return render_template('inspections.html', results=results, query=query)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/v1/inventory/check', methods=['POST'])
def api_check():
    # Undocumented API endpoint
    data = request.get_json()
    if not data or 'item_id' not in data:
        return jsonify({"error": "Missing item_id"}), 400
    
    raw_id = str(data['item_id'])
    # Apply the 'security' filter
    clean_id = security_filter(raw_id)
    
    db = get_db()
    try:
        # Vulnerable string formatting after a flawed filter
        query = f"SELECT id FROM shipments WHERE shipment_id = '{clean_id}'"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify({"status": "exists"})
        else:
            return jsonify({"status": "missing"})
    except Exception as e:
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "db": "connected"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)