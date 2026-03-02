import os
import sqlite3
import shutil
from flask import Flask, render_template, request, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DB_PATH = '/tmp/verdant.db'
TEMPLATE_DB = '/app/verdant.db'

def get_db_connection():
    # Ensure DB is in /tmp for read-only FS compatibility
    if not os.path.exists(DB_PATH):
        shutil.copy2(TEMPLATE_DB, DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(input_str):
    # Middle-tier security: Block common keywords followed by spaces/tabs
    blacklist = ['SELECT ', 'UNION ', 'WHERE ', 'FROM ', 'JOIN ', 'LIMIT ', 'OR ', 'AND ']
    for word in blacklist:
        if word in input_str.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = 'Guest Manager'
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/harvests')
def harvests():
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM harvest_records').fetchall()
    conn.close()
    return render_template('yields.html', records=records)

@app.route('/soil')
def soil():
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM soil_metrics').fetchall()
    conn.close()
    return render_template('soil.html', records=records)

@app.route('/reports')
def reports():
    sort_field = request.args.get('sort', 'crop_name')
    
    # The developer thought ORDER BY wasn't dangerous if spaces were blocked
    if not waf_check(sort_field):
        return "Security Violation: Malicious keywords detected.", 403

    try:
        conn = get_db_connection()
        # Vulnerable ORDER BY injection
        query = f"SELECT crop_name, yield, zone, harvest_date FROM harvest_records ORDER BY {sort_field} ASC"
        records = conn.execute(query).fetchall()
        conn.close()
    except Exception as e:
        return f"Database Error: {str(e)}", 500

    return render_template('reports.html', records=records, current_sort=sort_field)

@app.route('/api/status')
def status():
    return {"status": "online", "version": "2.4.1", "db_engine": "sqlite3"}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)