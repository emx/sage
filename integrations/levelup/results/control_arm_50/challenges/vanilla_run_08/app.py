import sqlite3
import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/verdant_pulse.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(data):
    # Rigid (but flawed) security policy engine
    bad_words = ["SELECT", "UNION", "WHERE", "FROM", "OR", "AND", "--", "DROP", "INSERT"]
    for word in bad_words:
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
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # VULNERABILITY: Raw string concatenation with data from the database (second-order)
    # The 'assigned_sector' was filtered on input, but is used unsafely here.
    try:
        query = f"SELECT * FROM soil_records WHERE sector_name = '{user['assigned_sector']}'"
        records = db.execute(query).fetchall()
    except Exception as e:
        records = []
        app.logger.error(f"DB Error: {e}")

    return render_template('dashboard.html', records=records, sector=user['assigned_sector'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    if request.method == 'POST':
        new_sector = request.form.get('sector')
        
        # Apply the 'Security Policy'
        if not security_filter(new_sector):
            flash('Security Policy Violation: Malicious keyword detected in sector name.', 'danger')
        else:
            db.execute('UPDATE users SET assigned_sector = ? WHERE id = ?', (new_sector, session['user_id']))
            db.commit()
            flash('Profile updated successfully.', 'success')
            
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/equipment')
def equipment():
    db = get_db()
    logs = db.execute('SELECT * FROM maintenance_logs LIMIT 10').fetchall()
    return render_template('equipment.html', logs=logs)

@app.route('/api/health')
def health():
    return {"status": "healthy", "engine": "VerdantPulse Core v2.4.1"}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)