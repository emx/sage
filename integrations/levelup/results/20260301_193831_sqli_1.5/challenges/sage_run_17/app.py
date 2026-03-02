import os
import sqlite3
import shutil
from flask import Flask, request, render_template, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "v3loce_str3am_logistics_2024_secret"

DB_SOURCE = '/app/velo_logistics.db'
DB_DEST = '/tmp/logistics.db'

def get_db_connection():
    # Ensure the database exists in the writable /tmp directory
    if not os.path.exists(DB_DEST):
        shutil.copyfile(DB_SOURCE, DB_DEST)
    conn = sqlite3.connect(DB_DEST)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    if not payload:
        return True
    blacklist = ['union', 'or', 'and', '--', '/*', ' ']
    for word in blacklist:
        if word in payload.lower():
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
        if username == 'driver_admin' and password == 'Veloce2024':
            session['user'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/tracking')
def tracking():
    tracking_id = request.args.get('id', '')
    result = None
    if tracking_id:
        conn = get_db_connection()
        # Secure tracking query
        result = conn.execute('SELECT * FROM cargo_items WHERE tracking_id = ?', (tracking_id,)).fetchone()
        conn.close()
    return render_template('tracking.html', result=result, tracking_id=tracking_id)

@app.route('/api/v1/shipments/analytics')
def api_analytics():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    sort_by = request.args.get('sort', 'id')
    
    if not waf_check(sort_by):
        return jsonify({"error": "Malicious input detected", "code": "WAF_BLOCK"}), 403

    try:
        conn = get_db_connection()
        # Vulnerable order by clause
        query = f"SELECT id, tracking_id, source_city, destination, ship_state FROM cargo_items ORDER BY {sort_by}"
        shipments = conn.execute(query).fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in shipments])
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/api/v1/shipments/search')
def api_search():
    q = request.args.get('q', '')
    conn = get_db_connection()
    results = conn.execute("SELECT tracking_id, ship_state FROM cargo_items WHERE tracking_id LIKE ?", (f"%{q}%",)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)