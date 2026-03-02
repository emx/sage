import sqlite3
import re
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/aetherflow.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(input_str):
    # A realistic but flawed WAF that looks for keywords followed by whitespace
    blacklist = ['SELECT', 'UNION', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'OR', 'AND']
    for word in blacklist:
        if re.search(rf"{word}\s", input_str, re.IGNORECASE):
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
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    pods = db.execute('SELECT * FROM pods LIMIT 5').fetchall()
    return render_template('dashboard.html', pods=pods)

@app.route('/pods')
def pods_list():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    pods = db.execute('SELECT * FROM pods').fetchall()
    return render_template('pods.html', pods=pods)

@app.route('/pod/<int:pod_id>')
def pod_detail(pod_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    pod = db.execute('SELECT * FROM pods WHERE id = ?', (pod_id,)).fetchone()
    return render_template('pod_detail.html', pod=pod)

@app.route('/api/v1/pod/<pod_id>/diagnostics')
def pod_diagnostics(pod_id):
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 403
    
    # The Vulnerability: String concatenation with a weak WAF
    if not waf_check(pod_id):
        return jsonify({"error": "Security Alert: Malicious activity detected"}), 400

    try:
        db = get_db()
        # Dangerous raw query
        query = f"SELECT sensor_type, value, reading_time FROM diagnostics WHERE pod_id = '{pod_id}'"
        results = db.execute(query).fetchall()
        
        if not results:
            return jsonify({"status": "error", "message": "No diagnostic data found for this pod ID"}), 404

        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"status": "error", "message": "Internal Database Error"}), 500

@app.route('/settings')
def settings():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)