import os
import sqlite3
import re
from flask import Flask, render_template, request, g, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
DATABASE = '/tmp/thalassa.db'

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
    if not payload:
        return True
    # Block spaces, UNION, and logical operators as whole words
    # Also block comments to prevent simple truncation
    bad_patterns = [
        r'\s', r'union', r'--', r'\bsleep\b', r'\bbenchmark\b', 
        r'\bor\b', r'\band\b', r'\bwaitfor\b'
    ]
    for pattern in bad_patterns:
        if re.search(pattern, payload, re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifests')
def manifests():
    sort_column = request.args.get('sort', 'id')
    
    if not waf_check(sort_column):
        return render_template('error.html', message="Security Alert: Malicious input detected by Sentinel WAF."), 403

    db = get_db()
    try:
        # Vulnerable ORDER BY injection point
        query = f"SELECT id, container_id, vessel, destination, status FROM shipments ORDER BY {sort_column}"
        cursor = db.execute(query)
        shipments = cursor.fetchall()
    except Exception as e:
        return render_template('error.html', message="Database Error: Contact your system administrator."), 500

    return render_template('manifests.html', shipments=shipments, current_sort=sort_column)

@app.route('/vessels')
def vessels():
    db = get_db()
    vessels = db.execute("SELECT * FROM vessels").fetchall()
    return render_template('fleet.html', vessels=vessels)

@app.route('/portal')
def login():
    return render_template('login.html')

@app.route('/api/status')
def status():
    return {"status": "online", "version": "2.4.1-stable", "waf": "Sentinel-v3"}

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)