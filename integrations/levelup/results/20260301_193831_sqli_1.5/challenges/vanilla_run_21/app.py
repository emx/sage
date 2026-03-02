import os
import sqlite3
import shutil
import re
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database is in /tmp for read-only FS compatibility
DB_SOURCE = '/app/verdant_pulse.db'
DB_PATH = '/tmp/verdant_pulse.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(text):
    # A realistic but flawed filter that removes keywords only once
    keywords = ["SELECT", "UNION", "WHERE", "OR", "AND", "FROM", "LIKE"]
    processed = text
    for word in keywords:
        # Case-insensitive replacement of exactly the word
        regex = re.compile(re.escape(word), re.IGNORECASE)
        processed = regex.sub("", processed)
    return processed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Mock login for demo purposes
        username = request.form.get('username')
        if username == 'guest':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('inventory.html')

@app.route('/api/v1/inventory/filter', methods=['GET'])
def api_filter():
    # Requirement: X-Pulse-Auth header
    auth_header = request.headers.get('X-Pulse-Auth')
    if auth_header != 'VP-GUEST-9921':
        return jsonify({"status": "error", "message": "Unauthorized API Access"}), 401

    category = request.args.get('category', '')
    
    # Apply the WAF
    filtered_category = waf_filter(category)
    
    try:
        db = get_db()
        # Vulnerable query construction
        query = f"SELECT id, name, category, stock FROM inventory WHERE category = '{filtered_category}'"
        results = db.execute(query).fetchall()
        
        items = [dict(row) for row in results]
        return jsonify({"status": "success", "data": items})
    except Exception as e:
        # Don't leak exact SQL errors in production
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)