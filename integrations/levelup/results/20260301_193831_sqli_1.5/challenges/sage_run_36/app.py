import sqlite3
import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(payload):
    # Mimic a WAF that blocks common SQLi keywords but misses specific subquery patterns
    blacklist = ['union', 'or ', ' or', 'and ', ' and', '--', '/*', '*/', 'sleep', 'benchmark', 'join']
    for word in blacklist:
        if word in payload.lower():
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

@app.route('/manifests')
def manifests():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    items = db.execute('SELECT * FROM manifests LIMIT 20').fetchall()
    return render_template('manifests.html', items=items)

@app.route('/personnel')
def personnel():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    drivers = db.execute('SELECT * FROM drivers').fetchall()
    return render_template('drivers.html', drivers=drivers)

@app.route('/reports/valuation')
def valuation_report():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    sort_column = request.args.get('sort', 'id')
    
    if not waf_check(sort_column):
        return render_template('error.html', message="Security Alert: Malicious activity detected in query parameters.")

    db = get_db()
    # VULNERABILITY: String interpolation into ORDER BY clause
    query = f"SELECT id, tracking_number, cargo_type, destination, valuation FROM manifests ORDER BY {sort_column}"
    
    try:
        results = db.execute(query).fetchall()
    except Exception as e:
        return render_template('error.html', message="Database error occurred during sorting.")

    return render_template('analytics.html', results=results, current_sort=sort_column)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/status')
def api_status():
    return {"status": "online", "version": "2.4.1-stable", "db": "connected"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)