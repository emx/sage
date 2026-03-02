import os
import sqlite3
import re
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "v3rd4nt_p4th_sup3r_s3cr3t_2024"
DB_PATH = "/tmp/verdant.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    if not payload:
        return True
    # Blacklist common SQL keywords if they are used as distinct words
    blacklist = ["SELECT", "UNION", "WHERE", "FROM", "LIMIT", "SLEEP", "JOIN", "OR", "AND"]
    for word in blacklist:
        if re.search(r'\b' + word + r'\b', payload.upper()):
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
        if username == 'guest' and password == 'guest':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('manifests.html')

@app.route('/drivers')
def drivers():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    drivers = db.execute("SELECT * FROM drivers").fetchall()
    return render_template('drivers.html', drivers=drivers)

@app.route('/maintenance')
def maintenance():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    logs = db.execute("SELECT * FROM maintenance_logs ORDER BY date DESC").fetchall()
    return render_template('maintenance.html', logs=logs)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['user'])

@app.route('/api/v1/shipping/query')
def shipping_query():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    sort_col = request.args.get('sort', 'id')
    
    # Vulnerable ORDER BY injection
    # The WAF check is present but bypassable using comments (/**/) or different syntax
    if not waf_filter(sort_col):
        return jsonify({"error": "Security Alert: Illegal keywords detected"}), 403

    try:
        db = get_db()
        # Dangerous string interpolation into SQL query
        query = f"SELECT * FROM manifests ORDER BY {sort_col} ASC"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error occurred"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)