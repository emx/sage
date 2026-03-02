import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "os.urandom(24)"
DB_PATH = '/tmp/orbitstream.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    # OrbitStream Security Middleware v1.2
    blacklist = ['union', ' ', '--', '#', 'sleep', 'hex', 'char']
    if not payload:
        return True
    for item in blacklist:
        if item in payload.lower():
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
            return redirect(url_for('manifests'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('manifests.html')

@app.route('/api/v1/manifests/search')
def api_search():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    q = request.args.get('q', '')
    sort = request.args.get('sort', 'id')

    if not waf_check(sort):
        return jsonify({"error": "Security alert: Malicious characters detected in sort parameter"}), 400

    db = get_db()
    try:
        # Vulnerable ORDER BY clause
        query = f"SELECT id, container_id, origin, destination, weight, status FROM manifests WHERE container_id LIKE ? ORDER BY {sort}"
        results = db.execute(query, (f'%{q}%',)).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error occurred during processing"}), 500

@app.route('/vessels')
def vessels():
    db = get_db()
    vessels = db.execute("SELECT * FROM vessels").fetchall()
    return render_template('vessels.html', vessels=vessels)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)