import os
import sqlite3
import shutil
import re
from flask import Flask, request, render_template, redirect, session, g

app = Flask(__name__)
app.secret_key = "vanguard_ultra_secret_67123"
DB_SOURCE = "/app/vanguard.db"
DB_PATH = "/tmp/vanguard.db"

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(DB_SOURCE, DB_PATH)
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# WAF Implementation
def waf_filter(payload):
    if not payload:
        return True
    # Block common SQLi keywords and spaces
    blacklist = [r"UNION", r"OR", r"\s", r"--", r"DROP", r"UPDATE"]
    for pattern in blacklist:
        if re.search(pattern, payload, re.IGNORECASE):
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
        if username == 'operator' and password == 'vanguard2024':
            session['user'] = 'operator'
            return redirect('/dashboard')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/search')
def search():
    if 'user' not in session:
        return redirect('/login')
    query = request.args.get('q', '')
    db = get_db()
    results = db.execute("SELECT * FROM containers WHERE container_id LIKE ?", ('%' + query + '%',)).fetchall()
    return render_template('search.html', results=results, query=query)

@app.route('/audit_logs')
def audit_logs():
    if 'user' not in session:
        return redirect('/login')
    
    op_id = request.args.get('id', '')
    
    if op_id and not waf_filter(op_id):
        return render_template('audit.html', error="Security Alert: Malicious Input Detected", logs=[])

    db = get_db()
    if op_id:
        # Vulnerable Sink
        query = f"SELECT * FROM audit_logs WHERE operator_id = {op_id}"
        try:
            logs = db.execute(query).fetchall()
        except Exception as e:
            return render_template('audit.html', error=f"Database Error", logs=[])
    else:
        logs = db.execute("SELECT * FROM audit_logs LIMIT 10").fetchall()
        
    return render_template('audit.html', logs=logs)

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /audit_logs", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)