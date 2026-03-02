import os
import sqlite3
import shutil
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "vanguard_logistics_ultra_secret_2024"
DATABASE = '/tmp/astravanguard.db'
TEMPLATE_DB = '/app/astravanguard_template.db'

def get_db():
    if not os.path.exists(DATABASE):
        shutil.copy(TEMPLATE_DB, DATABASE)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'guest' and password == 'guest':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/parts')
def parts():
    db = get_db()
    parts = db.execute('SELECT * FROM parts LIMIT 10').fetchall()
    return render_template('parts.html', parts=parts)

@app.route('/compliance')
def compliance():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('compliance.html')

@app.route('/api/v1/compliance/verify')
def api_verify():
    batch_id = request.args.get('batch_id', '')
    
    # Realistic WAF Filter
    blacklist = ['union', ' ', '--', '/*', 'or', 'sleep', 'benchmark']
    if any(x in batch_id.lower() for x in blacklist):
        return jsonify({"status": "error", "message": "Security Alert: Malicious characters detected"}), 403

    db = get_db()
    # VULNERABILITY: Direct interpolation into SQL query
    query = f"SELECT status, inspector FROM compliance_logs WHERE batch_id = '{batch_id}'"
    
    try:
        res = db.execute(query).fetchone()
        if res:
            return jsonify({"status": "compliant", "inspector": res['inspector'], "code": res['status']})
        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": "Database error occurred"}), 500

@app.route('/api/v1/system/health')
def health():
    return jsonify({"status": "online", "version": "2.4.1"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)