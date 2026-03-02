import sqlite3
import re
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = sqlite3.connect(Config.DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(value):
    # A custom WAF that blocks common SQL keywords and standard whitespace
    blacklist = [r'UNION\s+', r'SELECT\s+', r'UPDATE\s+', r'DELETE\s+', r'DROP\s+', r'OR\s+1=1', r'--']
    for pattern in blacklist:
        if re.search(pattern, value, re.IGNORECASE):
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    stats = {
        'total': db.execute('SELECT COUNT(*) FROM shipments').fetchone()[0],
        'active': db.execute('SELECT COUNT(*) FROM shipments WHERE status = "In Transit"').fetchone()[0]
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/shipments')
def shipments():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    items = db.execute('SELECT * FROM shipments').fetchall()
    return render_template('shipments.html', items=items)

@app.route('/reports')
def reports():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/api/v1/reports/custom', methods=['POST'])
def custom_report():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    sort_by = data.get('sort_by', 'id')
    direction = data.get('direction', 'ASC')

    # Vulnerable injection point
    if not waf_filter(sort_by):
        return jsonify({"error": "Security alert: Malicious activity detected"}), 403

    try:
        db = get_db()
        # Vulnerable query: sort_by is directly concatenated
        query = f"SELECT id, tracking_number, origin, destination, status FROM shipments ORDER BY {sort_by} {direction}"
        results = db.execute(query).fetchall()
        
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)