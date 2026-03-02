import sqlite3
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = sqlite3.connect(Config.DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def waf_check(payload):
    if not payload:
        return True
    # WAF blocks SQL keywords if they are followed by a space or are at word boundaries
    # This forces attackers to use comments or alternative spacing
    blacklist = ['SELECT', 'UNION', 'WHERE', 'FROM', 'AND', 'OR', 'LIKE', 'LIMIT']
    for word in blacklist:
        if re.search(rf'\b{word}\s+', payload, re.IGNORECASE):
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
    return render_template('dashboard.html')

@app.route('/shipments')
def shipments():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments LIMIT 20').fetchall()
    return render_template('shipments.html', shipments=shipments)

@app.route('/reports/fuel')
def fuel_reports():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    reports = db.execute('SELECT * FROM fuel_reports').fetchall()
    return render_template('reports.html', reports=reports)

@app.route('/archive/search')
def archive_search():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    cluster_id = request.headers.get('X-Backend-Cluster', '1')
    search_query = request.args.get('q', '')
    
    status = "Offline"
    cluster_name = "Unknown"

    if not waf_check(cluster_id):
        return render_template('archive.html', error="Security Violation: Malformed Cluster Header detected.")

    try:
        db = get_db()
        # Vulnerable Header Injection point
        query = f"SELECT cluster_name FROM clusters WHERE cluster_id = '{cluster_id}'"
        result = db.execute(query).fetchone()
        if result:
            status = "Active"
            cluster_name = result['cluster_name']
    except Exception as e:
        # Detailed errors disabled for production, but status reflects failure
        status = "Error"

    resp = make_response(render_template('archive.html', status=status, cluster=cluster_name, query=search_query))
    resp.headers['X-Backend-Cluster-Status'] = status
    return resp

@app.route('/api/health')
def health():
    return {"status": "healthy", "version": "2.4.1-legacy"}

if __name__ == '__main__':
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    app.run(host='0.0.0.0', port=5000)