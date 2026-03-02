import sqlite3
import os
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/astravantage.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(text):
    # A 'clever' WAF that strips dangerous keywords once
    # This is vulnerable to interleaved keywords like SELSELECTECT
    blacklist = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'FROM', 'LIMIT', 'SLEEP', '--', ' ']
    filtered = text
    for word in blacklist:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
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
        # Simple mock authentication for the demo
        if username == 'guest' and password == 'guest123':
            session['user'] = 'guest'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('inventory.html')

@app.route('/suppliers')
def suppliers():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    suppliers = db.execute('SELECT name, email, cert_level FROM suppliers').fetchall()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/shipping')
def shipping():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('shipping.html')

@app.route('/api/v1/inventory/search')
def api_search():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    query_param = request.args.get('q', '')
    # The WAF is applied here
    safe_query = waf_filter(query_param)
    
    try:
        db = get_db()
        # Vulnerable string concatenation after a weak WAF
        sql = f"SELECT id, name, serial, weight FROM components WHERE name LIKE '%{safe_query}%'"
        results = db.execute(sql).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)