import os
import sqlite3
import shutil
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_SOURCE = '/app/logistics.db'
DB_RUNTIME = '/tmp/logistics.db'

def get_db():
    if not os.path.exists(DB_RUNTIME):
        shutil.copy(DB_SOURCE, DB_RUNTIME)
    conn = sqlite3.connect(DB_RUNTIME)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(input_str):
    if not input_str:
        return True
    # Strict WAF for hard difficulty
    blacklist = [' ', '"', "'", '--', '/*', 'union', 'or', 'and']
    for item in blacklist:
        if item in input_str.lower():
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
        # Simple hardcoded guest login for the challenge flow
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

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/manifest/<int:id>')
def view_manifest(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifest = db.execute('SELECT * FROM manifests WHERE id = ?', (id,)).fetchone()
    if not manifest:
        return "Manifest not found", 404
    return render_template('manifest_view.html', manifest=manifest)

@app.route('/api/v1/telemetry', methods=['POST'])
def api_telemetry():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    manifest_id = data.get('manifest_id', 1)
    sort_by = data.get('sort_by', 'id')
    direction = data.get('order', 'ASC')

    if not waf_filter(sort_by):
        return jsonify({"error": "Security Alert: Malicious characters detected in sort_by"}), 403

    if direction.upper() not in ['ASC', 'DESC']:
        return jsonify({"error": "Invalid order direction"}), 400

    try:
        db = get_db()
        # Vulnerable ORDER BY injection point
        query = f"SELECT id, container_id, temperature, humidity, pressure FROM telemetry WHERE manifest_id = ? ORDER BY {sort_by} {direction}"
        results = db.execute(query, (manifest_id,)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database Error", "details": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "operational", "db_connected": os.path.exists(DB_RUNTIME)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)