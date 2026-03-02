import sqlite3
import os
from flask import Flask, render_template, request, jsonify, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(s):
    if not s:
        return False
    # Block common SQLi patterns and spaces
    blacklist = ['union', ' ', '--', '/*', 'where', 'join', 'sleep', 'benchmark', 'group', 'having']
    s_lower = s.lower()
    for item in blacklist:
        if item in s_lower:
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    parts = conn.execute('SELECT * FROM parts LIMIT 10').fetchall()
    conn.close()
    return render_template('inventory.html', parts=parts)

@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', error="Authentication service is temporarily down for maintenance.")

@app.route('/api/v1/health')
def health():
    return jsonify({"status": "operational", "engine": "NebulaCore-v4.2"})

@app.route('/api/v1/inventory/filter')
def inventory_filter():
    sort_by = request.args.get('sort', 'name')
    
    if waf_filter(sort_by):
        abort(403, description="Security Violation: Malicious patterns detected by NebulaWAF.")

    try:
        conn = get_db_connection()
        # The vulnerability: Unsafe string interpolation into ORDER BY
        query = f"SELECT id, name, category, stock_level FROM parts ORDER BY {sort_by} ASC"
        parts = conn.execute(query).fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in parts])
    except Exception as e:
        return jsonify({"error": "Invalid sort parameter", "details": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)