import os
import sqlite3
import shutil
from flask import Flask, render_template, request, g, redirect, url_for

app = Flask(__name__)
app.config.from_object('config.Config')

ORIGINAL_DB = '/app/data.db'
RUNTIME_DB = '/tmp/aether_acres.db'

def get_db():
    if not os.path.exists(RUNTIME_DB):
        shutil.copy(ORIGINAL_DB, RUNTIME_DB)
    
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(RUNTIME_DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(payload):
    if not payload:
        return True
    blacklist = [' ', 'UNION', 'OR']
    payload_upper = payload.upper()
    for word in blacklist:
        if word in payload_upper:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    token = request.headers.get('X-Regional-Token')
    user_data = None
    
    if token:
        if not waf_check(token):
            return "Security Violation Detected: Malicious Input Patterns Blocked.", 403
        
        db = get_db()
        try:
            # Vulnerable query
            query = f"SELECT username, region, role FROM coordinators WHERE auth_token = '{token}'"
            user_data = db.execute(query).fetchone()
        except Exception as e:
            return "Database Error: Internal Processing Exception", 500
            
    return render_template('dashboard.html', user=user_data)

@app.route('/manifests')
def manifests():
    db = get_db()
    search = request.args.get('q', '')
    if search:
        records = db.execute("SELECT * FROM manifests WHERE item LIKE ?", ('%' + search + '%',)).fetchall()
    else:
        records = db.execute("SELECT * FROM manifests LIMIT 10").fetchall()
    return render_template('manifests.html', records=records)

@app.route('/silos')
def silos():
    db = get_db()
    silo_data = db.execute("SELECT * FROM telemetry").fetchall()
    return render_template('silos.html', silos=silo_data)

@app.route('/profile/<int:id>')
def profile(id):
    db = get_db()
    profile = db.execute("SELECT * FROM coordinators WHERE id = ?", (id,)).fetchone()
    if not profile:
        return "Coordinator not found", 404
    return render_template('profile.html', profile=profile)

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)