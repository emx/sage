import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
DATABASE = '/tmp/veridian.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(payload):
    # Mimic a poorly implemented WAF that removes keywords once
    blacklist = ['SELECT', 'UNION', 'SLEEP', 'BENCHMARK', 'OR', 'AND', '--']
    processed = payload.upper()
    for word in blacklist:
        processed = processed.replace(word, '')
    return processed

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
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/fleet')
def fleet():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    drones = db.execute('SELECT * FROM drones').fetchall()
    return render_template('fleet.html', drones=drones)

@app.route('/maintenance')
def maintenance():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('maintenance.html')

@app.route('/api/v1/records/filter')
def api_filter():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    sort_by = request.args.get('sort', 'timestamp')
    # Vulnerability: The sort_by parameter is directly concatenated after a weak WAF check
    clean_sort = waf_filter(sort_by)
    
    query = f"SELECT * FROM maintenance_logs ORDER BY {clean_sort} ASC"
    
    try:
        db = get_db()
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({'error': 'Query execution failed', 'debug': str(e)} if app.debug else {'error': 'Internal Error'}), 500

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/status')
def status():
    return jsonify({'status': 'operational', 'nodes': 14, 'version': '2.4.1-stable'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)