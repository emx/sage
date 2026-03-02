import sqlite3
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = "4e7h3rf10w_53cr37_k3y_2024"
DATABASE = '/tmp/aetherflow.db'

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

def security_filter(text):
    # A simple but flawed security filter that strips dangerous keywords
    # This is vulnerable to nested keyword bypasses like UNUNIONION
    keywords = ['SELECT', 'UNION', 'FROM', 'WHERE', 'OR', 'AND', 'DROP', 'INSERT', 'UPDATE']
    filtered = text
    for kw in keywords:
        # Case-insensitive single-pass replacement
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        filtered = pattern.sub('', filtered)
    return filtered

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
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    if request.method == 'POST':
        region = request.form.get('region', '')
        display_name = request.form.get('display_name', '')
        
        # Apply the 'security filter' to the region
        safe_region = security_filter(region)
        
        db.execute('UPDATE users SET region = ?, display_name = ? WHERE id = ?', (safe_region, display_name, session['user_id']))
        db.commit()
        return render_template('profile.html', success="Profile updated successfully", user={'region': safe_region, 'display_name': display_name})

    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/shipments')
def shipments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT region FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # VULNERABILITY: Second-order SQL Injection
    # The 'region' value was filtered on input, but is now concatenated directly into a query
    query = f"SELECT tracking_id, origin, destination, status FROM shipments WHERE region = '{user['region']}'"
    
    try:
        shipments_data = db.execute(query).fetchall()
    except Exception as e:
        return f"Database Error: {str(e)}", 500
        
    return render_template('shipments.html', shipments=shipments_data)

@app.route('/fleet')
def fleet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    fleet_data = db.execute('SELECT * FROM fleet_metrics').fetchall()
    return render_template('fleet.html', fleet=fleet_data)

@app.route('/api/status')
def status():
    return {"status": "operational", "region": "Global"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)