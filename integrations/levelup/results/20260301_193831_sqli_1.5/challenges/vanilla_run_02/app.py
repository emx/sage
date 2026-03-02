import sqlite3
import re
import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from config import DATABASE, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def security_waf(val):
    if not val:
        return val
    # Vulnerable keyword removal: only replaces once, case-insensitive
    keywords = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'FROM', 'LIKE', 'LIMIT', 'JOIN']
    for k in keywords:
        val = re.sub(re.escape(k), '', val, flags=re.IGNORECASE)
    return val

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM vortex_users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        return render_template('index.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM vortex_manifests LIMIT 10').fetchall()
    return render_template('dashboard.html', manifests=manifests)

@app.route('/manifest/<id>')
def manifest_details(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifest = db.execute('SELECT * FROM vortex_manifests WHERE id = ?', (id,)).fetchone()
    return render_template('manifest.html', manifest=manifest)

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    items = db.execute('SELECT * FROM vortex_inventory').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/api/v1/vault/status')
def vault_status():
    # Hidden endpoint, vulnerable to Blind SQLi
    vault_id = request.args.get('vault_id', '')
    # Apply the 'security' filter
    safe_id = security_waf(vault_id)
    
    db = get_db()
    try:
        # Unsafe string formatting after WAF
        query = f"SELECT id FROM vortex_inventory WHERE id = '{safe_id}' AND item_type = 'Secure Vault'"
        res = db.execute(query).fetchone()
        if res:
            return jsonify({"status": "Active"})
        else:
            return jsonify({"status": "Invalid Vault ID"})
    except Exception as e:
        return jsonify({"status": "System Error"}), 500

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /api/v1/vault/status\nDisallow: /admin/config"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)