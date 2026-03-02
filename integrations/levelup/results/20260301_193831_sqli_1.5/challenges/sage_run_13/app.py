import sqlite3
import json
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, g
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/aerospace.db'

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

@app.before_request
def waf():
    # Security middleware: Checks the first 100 chars of POST data for SQL keywords
    if request.method == 'POST' and request.path == '/api/v1/logistics/search':
        raw_data = request.get_data(as_text=True)
        # VULNERABILITY: Only inspects the beginning of the request body
        inspection_zone = raw_data[:100].lower()
        blacklist = ['select', 'union', 'update', 'delete', 'where', 'and', 'or', 'join', '--']
        for word in blacklist:
            if word in inspection_zone:
                return jsonify({"error": "Security Violation", "message": f"Keyword '{word}' is prohibited."}), 403

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/units')
def units():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    units = db.execute('SELECT * FROM propulsion_units LIMIT 10').fetchall()
    return render_template('units.html', units=units)

@app.route('/unit/<serial_no>')
def unit_detail(serial_no):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    unit = db.execute('SELECT * FROM propulsion_units WHERE serial_no = ?', (serial_no,)).fetchone()
    return render_template('unit_details.html', unit=unit)

@app.route('/docs/api')
def api_docs():
    return render_template('docs.html')

@app.route('/api/v1/logistics/search', methods=['POST'])
def api_search():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        facility_id = data.get('facility_id', '')
        db = get_db()
        # VULNERABILITY: Direct string interpolation into SQL query
        query = f"SELECT serial_no, model, status FROM propulsion_units WHERE facility_id = '{facility_id}'"
        results = db.execute(query).fetchall()
        
        units_list = [dict(row) for row in results]
        return jsonify({"status": "success", "results": units_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)