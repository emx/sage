import sqlite3
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/aetherlink.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(input_str):
    # Simple WAF blocking common keywords followed by space or comments
    forbidden = ['SELECT ', 'UNION ', 'WHERE ', 'AND ', 'OR ', '--', '/*', 'INSERT ', 'UPDATE ', 'DELETE ']
    if any(keyword in input_str.upper() for keyword in forbidden):
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
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    satellites = db.execute('SELECT * FROM satellites').fetchall()
    return render_template('dashboard.html', satellites=satellites)

@app.route('/manifests')
def manifests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    query = request.args.get('q', '')
    if query:
        items = db.execute("SELECT * FROM manifests WHERE item_name LIKE ?", (f"%{query}%",)).fetchall()
    else:
        items = db.execute("SELECT * FROM manifests").fetchall()
    return render_template('manifests.html', items=items)

@app.route('/telemetry')
def telemetry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('telemetry.html')

@app.route('/api/v1/telemetry/data')
def api_telemetry():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    sat_id = request.args.get('sat_id', 1)
    sort_col = request.args.get('sort', 'timestamp')

    if not waf_check(sort_col):
        return jsonify({"error": "Security Violation: Forbidden characters detected in sort parameter"}), 400

    db = get_db()
    try:
        # VULNERABILITY: String concatenation in ORDER BY
        query = f"SELECT id, sensor, value, timestamp FROM telemetry WHERE sat_id = ? ORDER BY {sort_col}"
        results = db.execute(query, (sat_id,)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT username, role, email FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/logs')
def logs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    logs = db.execute('SELECT * FROM maintenance_logs ORDER BY created_at DESC').fetchall()
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)