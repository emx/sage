import os
import sqlite3
import shutil
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_SOURCE = '/app/aetherflow.db'
DB_PATH = '/tmp/aetherflow.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
        os.chmod(DB_PATH, 0o666)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    # WAF blocks common keywords followed by a space
    forbidden = ['SELECT ', 'UNION ', 'WHERE ', 'FROM ', 'OR ', 'AND ', 'LIMIT ', 'OFFSET ']
    if not payload:
        return True
    p_upper = payload.upper()
    for word in forbidden:
        if word in p_upper:
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
            session['user'] = user['username']
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
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM shipping_manifests ORDER BY arrival_date DESC').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/vessels')
def vessels():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    vessels = db.execute('SELECT * FROM port_registry').fetchall()
    return render_template('vessels.html', vessels=vessels)

@app.route('/api/v1/vessel/metrics')
def vessel_metrics():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    v_id = request.args.get('vessel_id', '')
    
    if not waf_check(v_id):
        return jsonify({"error": "Security violation detected. Potential SQL injection blocked."}), 403

    db = get_db()
    # VULNERABLE QUERY: String concatenation used for metrics lookup
    query = f"SELECT metric_name, metric_value FROM vessel_metrics WHERE vessel_id = '{v_id}'"
    
    try:
        metrics = db.execute(query).fetchall()
        if not metrics:
            return jsonify({"status": "no_data", "metrics": []})
        
        result = []
        for m in metrics:
            result.append({"name": m[0], "value": m[1]})
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": "Internal Database Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)