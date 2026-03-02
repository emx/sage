import sqlite3
import re
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "v3lo_l1nk_secret_2024_key_!"
DB_PATH = '/tmp/velolink.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    # Rejects SQL keywords followed by whitespace
    blacklist = ['SELECT', 'UNION', 'FROM', 'WHERE', 'HAVING', 'GROUP', 'ORDER', 'LIMIT', 'INSERT', 'UPDATE', 'DELETE']
    for word in blacklist:
        if re.search(rf"{word}\s+", payload, re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Secure login
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/shipments')
def shipments():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    shipments = conn.execute('SELECT * FROM shipments LIMIT 10').fetchall()
    conn.close()
    return render_template('shipments.html', shipments=shipments)

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('inventory.html')

@app.route('/api/v1/nodes/status')
def node_status():
    # Internal API for warehouse managers
    node_id = request.args.get('node_id', '')
    
    if not waf_filter(node_id):
        return jsonify({"error": "Security Violation Detected", "status": "BLOCKED"}), 403

    try:
        conn = get_db_connection()
        # Unsafe string concatenation in internal-only management API
        query = f"SELECT node_name FROM warehouse_nodes WHERE id = '{node_id}'"
        result = conn.execute(query).fetchone()
        conn.close()

        if result:
            return jsonify({"node": result['node_name'], "status": "ACTIVE"})
        else:
            return jsonify({"status": "OFFLINE"})
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)