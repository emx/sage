import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, g
import os
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/verdaroot.db'

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

def security_filter(payload):
    # WAF: Blacklist spaces and common SQL keywords used in UNION based attacks
    blacklist = [r'\s+', r'union', r'or', r'and', r'--', r'\/\*']
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
        # Simple hardcoded check for demo purposes
        if username == 'guest' and password == 'guest123':
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

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('inventory.html')

@app.route('/batch/<int:batch_id>')
def batch_detail(batch_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    batch = db.execute('SELECT * FROM seed_batches WHERE batch_id = ?', (batch_id,)).fetchone()
    if batch:
        return render_template('batch_detail.html', batch=batch)
    return "Batch not found", 404

@app.route('/api/v1/inventory/search')
def api_search():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    sort_field = request.args.get('sort', 'batch_id')
    
    # Defense: Security filter (WAF)
    if not security_filter(sort_field):
        return jsonify({"error": "Security alert: Illegal characters or keywords detected in sort parameter"}), 400

    db = get_db()
    try:
        # VULNERABILITY: sort_field is concatenated directly into ORDER BY
        query = f"SELECT batch_id, strain_name, moisture, warehouse FROM seed_batches ORDER BY {sort_field} ASC"
        cursor = db.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html', message="Access restricted to system administrators.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)