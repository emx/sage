from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    # Hardened WAF: Blocks common keywords but misses CASE/WHEN and allows subqueries
    # Using word boundaries to be more realistic
    blacklist = [r'\bUNION\b', r'\bOR\b', r'\bAND\b', r'--', r'/\*', r'\bSLEEP\b', r'\bBENCHMARK\b', r'\bJOIN\b']
    for pattern in blacklist:
        if re.search(pattern, payload, re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simple mock login for functionality
        session['user'] = 'Technician_7'
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    query = request.args.get('q', '')
    conn = get_db_connection()
    # Secure parameterized query for the main search
    parts = conn.execute('SELECT * FROM components WHERE part_name LIKE ?', ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('inventory.html', parts=parts, query=query)

@app.route('/api/v1/internal/component_report')
def component_report():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    sort_col = request.args.get('sort', 'part_name')
    
    if not waf_check(sort_col):
        return jsonify({"error": "Security alert: Malicious characters detected"}), 400

    conn = get_db_connection()
    try:
        # VULNERABLE: Direct string interpolation into ORDER BY clause
        query = f"SELECT part_id, part_name, serial_number, stock_level FROM components ORDER BY {sort_col} ASC"
        results = conn.execute(query).fetchall()
        data = [dict(row) for row in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)