import sqlite3
import os
import shutil
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure DB is in /tmp for write access on read-only FS
DB_PATH = '/tmp/thalassa.db'
TEMPLATE_DB = '/app/thalassa_template.db'

def init_runtime_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(TEMPLATE_DB, DB_PATH)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(payload):
    # A realistic 'bad' filter that strips keywords but not recursively
    forbidden = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'FROM', 'SLEEP']
    result = payload
    for word in forbidden:
        # Case insensitive replacement with empty string
        import re
        result = re.sub(re.escape(word), '', result, flags=re.IGNORECASE)
    # Also block spaces to force alternate bypasses
    return result.replace(' ', '')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vessels')
def vessels():
    db = get_db()
    vessels = db.execute('SELECT * FROM vessels').fetchall()
    return render_template('vessels.html', vessels=vessels)

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    if request.method == 'POST':
        query = request.form.get('query', '')
        db = get_db()
        # Safe query for the public search
        results = db.execute('SELECT * FROM containers WHERE tracking_id LIKE ?', ('%' + query + '%',)).fetchall()
    return render_template('search.html', results=results)

@app.route('/manifests')
def manifests():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'logistream_secure_2024':
            session['logged_in'] = True
            return redirect(url_for('manifests'))
    return render_template('login.html')

@app.route('/api/v1/manifest/verify', methods=['POST'])
def verify_manifest():
    # Legacy endpoint discovered via source comments
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Missing manifest ID'}), 400
    
    raw_id = str(data['id'])
    filtered_id = waf_filter(raw_id)
    
    db = get_db()
    try:
        # Vulnerable sink
        query = f"SELECT id FROM manifests WHERE manifest_id = '{filtered_id}'"
        result = db.execute(query).fetchone()
        if result:
            return jsonify({'status': 'valid', 'message': 'Manifest integrity verified'})
        else:
            return jsonify({'status': 'invalid', 'message': 'Manifest ID not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal database error'}), 500

if __name__ == '__main__':
    init_runtime_db()
    app.run(host='0.0.0.0', port=5000)