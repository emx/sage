import sqlite3
import os
import re
from flask import Flask, render_template, request, session, redirect, g

app = Flask(__name__)
app.config.from_object('config.Config')

DATABASE = '/tmp/zenith_aura.db'

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

def waf_filter(input_str):
    # Hardened WAF: No spaces, no UNION
    blacklist = ['union', ' ', '\t', '\n', '\r', '\v', '\f']
    for word in blacklist:
        if word in input_str.lower():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifests')
def manifests():
    db = get_db()
    manifests = db.execute('SELECT * FROM satellite_manifests LIMIT 10').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/schedule')
def schedule():
    db = get_db()
    windows = db.execute('SELECT * FROM launch_windows ORDER BY window_start ASC').fetchall()
    return render_template('schedule.html', windows=windows)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple mock auth
        if username == 'guest' and password == 'guest123':
            session['user'] = 'guest'
            session['role'] = 'viewer'
            return redirect('/portal/dashboard')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/portal/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/portal/telemetry/check')
def telemetry_check():
    if 'user' not in session:
        return "Unauthorized", 403
    
    node_id = request.args.get('node_id', '')
    if not node_id:
        return "Missing node_id parameter", 400

    if not waf_filter(node_id):
        return "Security Alert: Malicious pattern detected in node_id", 400

    db = get_db()
    try:
        # Vulnerable query: node_id is concatenated directly and allows comments for space bypass
        query = f"SELECT status FROM system_nodes WHERE node_id = {node_id}"
        result = db.execute(query).fetchone()
        
        if result and result['status'] == 'ACTIVE':
            return render_template('telemetry.html', status="ACTIVE", node=node_id)
        else:
            return render_template('telemetry.html', status="INACTIVE", node=node_id)
    except Exception as e:
        # Blind SQLi often results in errors being suppressed or generic
        return render_template('telemetry.html', status="ERROR", node=node_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)