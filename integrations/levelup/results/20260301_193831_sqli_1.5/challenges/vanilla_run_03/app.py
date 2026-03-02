import os
import sqlite3
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def waf_check(payload):
    # Rejects common SQL keywords if they are followed by whitespace
    blacklist = [r'SELECT\s+', r'UNION\s+', r'FROM\s+', r'WHERE\s+', r'OR\s+', r'AND\s+']
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
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM dispatchers WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
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
    manifests = db.execute('SELECT * FROM manifests LIMIT 20').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/drivers')
def drivers():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    drivers = db.execute('SELECT * FROM drivers').fetchall()
    return render_template('drivers.html', drivers=drivers)

@app.route('/api/v1/debug/node_diagnostics')
def diagnostics():
    if 'user_id' not in session: 
        return jsonify({"error": "Unauthorized"}), 403
    
    sort_by = request.args.get('sort_by', 'id')
    
    # Vulnerable ORDER BY injection
    if not waf_check(sort_by):
        return jsonify({"error": "Security filter triggered", "detail": "Forbidden keywords detected"}), 400

    try:
        db = get_db()
        # The vulnerability: direct string interpolation into the ORDER BY clause
        query = f"SELECT id, node_name, status, load_factor FROM shipping_nodes ORDER BY {sort_by}"
        nodes = db.execute(query).fetchall()
        return jsonify([dict(n) for n in nodes])
    except Exception as e:
        return jsonify({"error": "Database error", "msg": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)