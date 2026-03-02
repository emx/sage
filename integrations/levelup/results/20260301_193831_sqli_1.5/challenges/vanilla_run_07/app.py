import sqlite3
import base64
import os
from flask import Flask, request, render_template, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = "AetherLink_Secret_2024_Key"
DATABASE = "/tmp/aetherlink.db"

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

def waf_check(payload):
    blacklist = ['union', 'where', 'or ', ' or', '--', '/*', '*/', 'sleep']
    for word in blacklist:
        if word in payload.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track')
def track():
    return render_template('track.html')

@app.route('/portal/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'guest' and password == 'guest_aether2024':
            session['user'] = 'Guest Partner'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/portal/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/portal/shipments')
def shipments():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    items = db.execute("SELECT * FROM shipment_records LIMIT 10").fetchall()
    return render_template('shipments.html', items=items)

@app.route('/portal/telemetry')
def telemetry():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    sort_b64 = request.args.get('sort', 'dGltZXN0YW1w') # default 'timestamp'
    try:
        sort_col = base64.b64decode(sort_b64).decode('utf-8')
    except:
        sort_col = 'timestamp'

    if not waf_check(sort_col):
        return render_template('error.html', message="Security Alert: Malicious pattern detected."), 403

    db = get_db()
    # Vulnerable ORDER BY injection
    query = f"SELECT shipment_id, sensor_type, reading, timestamp FROM telemetry_logs ORDER BY {sort_col} ASC"
    try:
        logs = db.execute(query).fetchall()
    except Exception as e:
        return render_template('error.html', message="Database Error in reporting engine."), 500

    return render_template('telemetry.html', logs=logs, current_sort=sort_b64)

@app.route('/api/status')
def status():
    return {"status": "operational", "version": "2.4.1-legacy"}

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)