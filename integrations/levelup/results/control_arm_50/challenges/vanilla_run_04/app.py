import os
import sqlite3
import re
from flask import Flask, request, session, redirect, render_template, g, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/verdant.db'

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

def waf_check(data):
    # Intentional flaw: Case-sensitive check against a blacklist
    prohibited = ["SELECT", "UNION", "FROM", "WHERE", "OR", "AND", "--", "/*"]
    for word in prohibited:
        if word in data:
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
            return redirect('/dashboard')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    db = get_db()
    # Retrieve the user's saved monitoring region
    region_row = db.execute('SELECT region_name FROM saved_regions WHERE user_id = ?', (session['user_id'],)).fetchone()
    region_name = region_row['region_name'] if region_row else "Global"
    
    # Vulnerable Second-Order Injection Point
    # The region_name is injected directly into the query
    try:
        query = f"SELECT COUNT(*) as count FROM soil_metrics WHERE region = '{region_name}'"
        result = db.execute(query).fetchone()
        sensor_count = result['count']
    except Exception as e:
        sensor_count = "Error"
        
    return render_template('dashboard.html', region=region_name, sensor_count=sensor_count)

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    metrics = db.execute('SELECT * FROM soil_metrics LIMIT 10').fetchall()
    return render_template('analytics.html', metrics=metrics)

@app.route('/api/v1/region', methods=['POST'])
def update_region():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    region_name = request.form.get('region_name', '')
    
    # The WAF is flawed because it only checks uppercase variants
    if not waf_check(region_name):
        return jsonify({"status": "error", "message": "Security filter triggered! No SQL allowed."}), 400
    
    db = get_db()
    # Update or insert region
    existing = db.execute('SELECT id FROM saved_regions WHERE user_id = ?', (session['user_id'],)).fetchone()
    if existing:
        db.execute('UPDATE saved_regions SET region_name = ? WHERE user_id = ?', (region_name, session['user_id']))
    else:
        db.execute('INSERT INTO saved_regions (user_id, region_name) VALUES (?, ?)', (session['user_id'], region_name))
    db.commit()
    
    return jsonify({"status": "success", "region": region_name})

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('profile.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)