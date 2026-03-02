import sqlite3
import re
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(input_str):
    # Blacklist common SQL injection keywords and characters
    # Players must use boolean-based techniques and avoid these keywords
    blacklist = [r'UNION', r'JOIN', r'--', r'#', r'\/\*', r'\*\/', r'\bOR\b', r'\bAND\b']
    if input_str:
        for pattern in blacklist:
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
        
        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        db.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
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
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    regions = db.execute('SELECT * FROM regions').fetchall()
    db.close()
    return render_template('analytics.html', regions=regions)

@app.route('/api/v1/yield_data')
def yield_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    region_id = request.args.get('region_id', '1')
    sort_col = request.args.get('sort', 'year')

    # Validate region_id is numeric
    if not region_id.isdigit():
        return jsonify({"error": "Invalid region ID"}), 400

    # WAF Check on the sort column
    if not waf_filter(sort_col):
        return jsonify({"error": "Security block: Prohibited characters detected in sort parameter"}), 403

    try:
        db = get_db_connection()
        # VULNERABILITY: sort_col is concatenated directly into the ORDER BY clause
        query = f"SELECT * FROM crop_yields WHERE region_id = {region_id} ORDER BY {sort_col}"
        results = db.execute(query).fetchall()
        db.close()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/sensors')
def sensors():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    sensor_data = db.execute('SELECT * FROM sensors LIMIT 20').fetchall()
    db.close()
    return render_template('sensors.html', sensors=sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)