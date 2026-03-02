import sqlite3
import os
import re
import shutil
from flask import Flask, render_template, request, g

app = Flask(__name__)
app.config['SECRET_KEY'] = '55d8e7b9231f4e8ea312b9195679c45a'
DB_SOURCE = 'vexillum.db'
DB_PATH = '/tmp/vexillum.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copyfile(DB_SOURCE, DB_PATH)
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

def waf_filter(payload):
    if not payload: return ""
    # A single-pass filter that strips common SQL keywords
    keywords = ['SELECT', 'FROM', 'UNION', 'WHERE', 'AND', 'OR', 'LIKE', 'JOIN', 'SLEEP']
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        payload = pattern.sub('', payload)
    return payload

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/manifests')
def manifests():
    db = get_db()
    items = db.execute('SELECT * FROM shipments LIMIT 10').fetchall()
    return render_template('manifests.html', items=items)

@app.route('/fleet')
def fleet():
    db = get_db()
    vessels = db.execute('SELECT * FROM vessels').fetchall()
    return render_template('fleet.html', vessels=vessels)

@app.route('/portal/login')
def login():
    return render_template('login.html')

@app.route('/portal/audit')
def audit():
    audit_id = request.args.get('id', '')
    if not audit_id:
        return render_template('audit.html', result=None)

    # Vulnerable processing: WAF can be bypassed by nesting keywords
    processed_id = waf_filter(audit_id)
    
    db = get_db()
    try:
        # Unsafe string formatting
        query = f"SELECT status FROM audit_logs WHERE log_id = '{processed_id}'"
        result = db.execute(query).fetchone()
        if result:
            status = "ACTIVE"
        else:
            status = "NOT_FOUND"
    except Exception as e:
        status = "ERROR"

    return render_template('audit.html', result=status)

@app.route('/api/health')
def health():
    return {"status": "online", "nodes": 12, "db_connected": True}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)