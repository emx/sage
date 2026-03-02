import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(payload):
    # WAF: Blocks common SQLi keywords and whitespace techniques
    blacklist = ['UNION', 'OR', '--', '/*', '#', ' ', 'SLEEP', 'BENCHMARK', 'WAITFOR']
    if not payload:
        return True
    for word in blacklist:
        if word in payload.upper():
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
        
        if username == 'guest' and password == 'guest':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/vessels')
def vessels():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    vessels = conn.execute('SELECT * FROM vessels LIMIT 10').fetchall()
    conn.close()
    return render_template('vessels.html', vessels=vessels)

@app.route('/vessel/<int:vessel_id>')
def vessel_detail(vessel_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    vessel = conn.execute('SELECT * FROM vessels WHERE id = ?', (vessel_id,)).fetchone()
    manifests = conn.execute('SELECT * FROM manifests WHERE vessel_id = ?', (vessel_id,)).fetchall()
    conn.close()
    if not vessel:
        return "Vessel not found", 404
    return render_template('vessel.html', vessel=vessel, manifests=manifests)

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    sort_column = request.args.get('sort', 'id')
    
    if not security_filter(sort_column):
        return render_template('error.html', message="Security Violation: Malicious patterns detected in request."), 403

    conn = get_db_connection()
    # VULNERABILITY: String interpolation in ORDER BY clause
    try:
        query = f"SELECT * FROM manifests ORDER BY {sort_column} ASC"
        manifests = conn.execute(query).fetchall()
    except Exception as e:
        conn.close()
        return render_template('error.html', message="Database error occurred during sorting."), 500
    
    conn.close()
    return render_template('manifests.html', manifests=manifests)

@app.route('/compliance')
def compliance():
    return render_template('compliance.html')

@app.route('/api/v1/stats')
def api_stats():
    return {"status": "operational", "vessels_tracked": 1420, "active_manifests": 89212}

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)