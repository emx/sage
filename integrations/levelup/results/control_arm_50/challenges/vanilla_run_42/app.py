import sqlite3
import re
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = sqlite3.connect(Config.DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(input_str):
    # Simulate a strict WAF that blocks keywords and spaces
    blacklist = ['SELECT', 'FROM', 'WHERE', 'UNION', 'JOIN', 'SLEEP', 'OR', 'AND', '--']
    if any(keyword in input_str.upper() for keyword in blacklist):
        # Basic bypass check: permit if it uses SQL comments for obfuscation
        if '/**/' not in input_str:
            return False
    if ' ' in input_str:
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
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/telemetry')
def telemetry():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('telemetry.html')

@app.route('/api/v1/archive')
def api_archive():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    sort_column = request.args.get('sort', 'timestamp')
    
    # The Vulnerability: Order By Injection
    if not waf_filter(sort_column):
        return jsonify({"error": "Security Alert: Malicious pattern detected"}), 403

    try:
        db = get_db()
        # Dangerous string concatenation in ORDER BY
        query = f"SELECT cargo_id, destination, timestamp FROM manifests ORDER BY {sort_column}"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

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