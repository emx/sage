import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
DATABASE = config.DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(payload):
    # Corporate WAF: Block common SQLi patterns and spaces
    blacklist = [' ', '--', '/*', '*/', 'union', 'or', 'and', 'sleep', 'benchmark', 'join']
    if not payload:
        return True
    p_low = payload.lower()
    for word in blacklist:
        if word in p_low:
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
        
        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        db.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
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

@app.route('/manifests')
def manifests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    sort_by = request.args.get('sort', 'id')
    
    if not security_filter(sort_by):
        return render_template('error.html', message="Security Violation: Malicious characters detected in sort parameter."), 403

    db = get_db_connection()
    try:
        # Vulnerable order by injection
        query = f"SELECT id, manifest_id, vessel_name, destination, status FROM manifests ORDER BY {sort_by}"
        shipments = db.execute(query).fetchall()
    except Exception as e:
        return render_template('error.html', message="Database Error: Query execution failed."), 500
    finally:
        db.close()
        
    return render_template('manifests.html', shipments=shipments, current_sort=sort_by)

@app.route('/vessels')
def vessels():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    vessels = db.execute('SELECT * FROM vessel_registry').fetchall()
    db.close()
    return render_template('vessels.html', vessels=vessels)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/api/status')
def api_status():
    return {"status": "operational", "version": "2.4.1-stable", "node": "AL-LOG-01"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)