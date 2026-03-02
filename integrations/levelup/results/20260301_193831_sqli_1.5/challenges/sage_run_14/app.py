import sqlite3
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(input_str):
    # Hardened WAF: Blocks common keywords and comment symbols
    # Note: Using regex to detect whole words only to avoid false positives like 'ORDER'
    waf_blocklist = [r'\bUNION\b', r'\bWHERE\b', r'\bOR\b', r'\bAND\b', r'--', r'/\*', r';']
    if not input_str:
        return True
    for pattern in waf_blocklist:
        if re.search(pattern, input_str.upper()):
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
        # Simple authentication for demo purposes
        if username == 'guest' and password == 'VeloceGuest2024!':
            session['user'] = 'guest'
            session['role'] = 'dispatcher'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/fleet')
def fleet():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('fleet.html')

@app.route('/api/v1/vessels/filter')
def filter_vessels():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    sort_by = request.args.get('sort', 'vessel_name')
    
    if not security_filter(sort_by):
        return jsonify({"error": "Security filter triggered: Potential SQL Injection detected"}), 403

    conn = get_db_connection()
    try:
        # Vulnerable ORDER BY injection point
        query = f"SELECT * FROM vessels ORDER BY {sort_by} ASC"
        vessels = conn.execute(query).fetchall()
        return jsonify([dict(v) for v in vessels])
    except Exception as e:
        return jsonify({"error": "Database error", "msg": str(e)}), 500
    finally:
        conn.close()

@app.route('/manifest/<manifest_id>')
def manifest(manifest_id):
    # Static manifest viewer for narrative immersion
    return render_template('manifest.html', manifest_id=manifest_id)

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)