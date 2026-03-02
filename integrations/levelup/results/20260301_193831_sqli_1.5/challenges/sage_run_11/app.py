import sqlite3
import re
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB_PATH = '/tmp/orbit_logistics.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(data):
    # WAF: Blacklist keywords using word boundaries
    # Bypass: Use /**/ to break the regex word boundary check
    blacklist = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'FROM', 'LIMIT', 'OFFSET', 'JOIN', 'SLEEP']
    for word in blacklist:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, data, re.IGNORECASE):
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
        if username == 'admin' and password == 'OrbitStream2024!':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    manifests = conn.execute('SELECT * FROM manifests').fetchall()
    conn.close()
    return render_template('dashboard.html', manifests=manifests)

@app.route('/manifest/<int:manifest_id>')
def manifest_detail(manifest_id):
    conn = get_db_connection()
    manifest = conn.execute('SELECT * FROM manifests WHERE id = ?', (manifest_id,)).fetchone()
    conn.close()
    if manifest is None:
        return "Manifest not found", 404
    return render_template('details.html', manifest=manifest)

@app.route('/tracking')
def tracking():
    container_id = request.args.get('cid', '')
    return render_template('track.html', container_id=container_id)

@app.route('/docs')
def documentation():
    return render_template('docs.html')

@app.route('/api/v1/verify_integrity', methods=['POST'])
def verify_integrity():
    data = request.get_json()
    if not data or 'container_id' not in data:
        return jsonify({'error': 'Missing container_id'}), 400
    
    container_id = str(data.get('container_id'))
    
    if not security_filter(container_id):
        return jsonify({'error': 'Security violation detected', 'code': 'WAF_BLOCK'}), 403

    try:
        conn = get_db_connection()
        # Vulnerable Sink
        query = f"SELECT id FROM manifests WHERE container_id = '{container_id}' AND status = 'Verified'"
        result = conn.execute(query).fetchone()
        conn.close()
        
        if result:
            return jsonify({'valid': True, 'status': 'Manifest integrity confirmed'})
        else:
            return jsonify({'valid': False, 'status': 'Integrity mismatch or manifest not verified'})
    except Exception as e:
        return jsonify({'error': 'Database processing error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)