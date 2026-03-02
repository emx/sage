import os
import sqlite3
import shutil
from flask import Flask, request, render_template, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure database is in /tmp for write access if needed, though we use it mostly RO
DB_SOURCE = '/app/vesper.db'
DB_PATH = '/tmp/vesper.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(s):
    if not s:
        return True
    # Realistic WAF blocking common SQLi patterns
    blacklist = ['union', '--', '#', '/*', 'benchmark', 'sleep']
    forbidden_chars = [' ']
    
    s_lower = s.lower()
    for item in blacklist:
        if item in s_lower:
            return False
    for char in forbidden_chars:
        if char in s:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/estates')
def estates():
    db = get_db()
    items = db.execute('SELECT * FROM estates LIMIT 10').fetchall()
    return render_template('estates.html', estates=items)

@app.route('/estates/<int:estate_id>')
def estate_details(estate_id):
    db = get_db()
    estate = db.execute('SELECT * FROM estates WHERE id = ?', (estate_id,)).fetchone()
    if not estate:
        return "Not Found", 404
    return render_template('details.html', estate=estate)

@app.route('/api/v1/estates/search', methods=['POST'])
def api_search():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    query_filter = data.get('filter', '')
    sort_by = data.get('sort', 'name')

    if not waf_check(sort_by):
        return jsonify({"error": "Security Alert: Malicious input detected in sort parameter"}), 403

    # Vulnerable ORDER BY injection
    # WAF blocks spaces, so attacker must use \t, \n, or other whitespace
    try:
        db = get_db()
        sql = f"SELECT id, name, location, price FROM estates WHERE location LIKE ? ORDER BY {sort_by}"
        results = db.execute(sql, (f"%{query_filter}%",)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    bookings = db.execute('SELECT b.*, e.name FROM bookings b JOIN estates e ON b.estate_id = e.id WHERE b.user_id = ?', (session['user_id'],)).fetchall()
    return render_template('dashboard.html', user=user, bookings=bookings)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)