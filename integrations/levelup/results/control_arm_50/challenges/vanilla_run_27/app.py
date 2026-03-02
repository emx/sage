import sqlite3
import os
import shutil
from flask import Flask, render_template, request, redirect, session, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DB_PATH = '/tmp/vantage.db'
ORIGINAL_DB = '/app/vantage.db'

def get_db():
    if not os.path.exists(DB_PATH):
        shutil.copy(ORIGINAL_DB, DB_PATH)
        os.chmod(DB_PATH, 0o666)
    
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def security_filter(s):
    if not s:
        return True
    blacklist = ['UNION', 'OR', 'UPDATE', 'DELETE', 'DROP', 'INSERT', '--', ' #', '/*', '*/']
    for word in blacklist:
        if word in s.upper():
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
    return render_template('dashboard.html')

@app.route('/manifests')
def manifests():
    if 'user_id' not in session:
        return redirect('/login')
    
    sort_col = request.args.get('sort', 'id')
    
    if not security_filter(sort_col):
        return render_template('error.html', message="Security violation detected by VantageShield WAF.")

    db = get_db()
    # Vulnerable ORDER BY injection
    try:
        query = f"SELECT * FROM manifests ORDER BY {sort_col} ASC"
        manifest_list = db.execute(query).fetchall()
    except Exception as e:
        return render_template('error.html', message="Database error occurred during sorting.")

    return render_template('manifests.html', manifests=manifest_list, current_sort=sort_col)

@app.route('/inventory')
def inventory():
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    items = db.execute('SELECT * FROM inventory').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/api/v1/carrier/check')
def carrier_check():
    # Realistic hidden-ish endpoint
    carrier_id = request.args.get('id', '')
    db = get_db()
    carrier = db.execute('SELECT name, region, status FROM carriers WHERE carrier_id = ?', (carrier_id,)).fetchone()
    if carrier:
        return {"name": carrier['name'], "status": carrier['status'], "region": carrier['region']}
    return {"error": "Carrier not found"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)