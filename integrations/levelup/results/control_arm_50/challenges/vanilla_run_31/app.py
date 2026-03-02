import sqlite3
import os
import shutil
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_SOURCE = '/app/production.db'
DB_PATH = '/tmp/aetheria.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
        os.chmod(DB_PATH, 0o666)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    if not payload:
        return True
    # Strict blacklist for word-boundary keywords and spaces
    forbidden = ['UNION', 'WHERE', 'AND', 'OR', ' ', '--', '/*', '*/', 'LIMIT', 'OFFSET']
    p = str(payload).upper()
    for word in forbidden:
        if word in p:
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
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/nodes')
def nodes():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    nodes = db.execute('SELECT * FROM nodes').fetchall()
    return render_template('nodes.html', nodes=nodes)

@app.route('/api/v1/nodes/diagnostic')
def node_diagnostic():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    node_id = request.args.get('node_id', '')
    
    if not waf_check(node_id):
        return jsonify({'error': 'Security violation detected by WAF', 'status': 'blocked'}), 403

    db = get_db()
    try:
        # Intentionally vulnerable to SQL injection
        query = f"SELECT * FROM nodes WHERE id = {node_id}"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify({
                'status': 'Healthy',
                'node': result['node_name'],
                'uptime': '99.9%'
            })
        else:
            return jsonify({'status': 'Offline', 'error': 'Node not found'})
    except Exception as e:
        return jsonify({'status': 'Error', 'message': 'Internal Query Error'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)