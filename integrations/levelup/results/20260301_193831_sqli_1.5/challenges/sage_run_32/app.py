import sqlite3
import os
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(input_str):
    # WAF: Blocks spaces, comments, UNION, OR, and common SQL characters
    if not input_str:
        return True
    blacklist = [' ', '--', ';', 'union', 'or ', ' or', 'waitfor', 'delay', 'sleep', '"', 'load_file']
    for item in blacklist:
        if item in input_str.lower():
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

@app.route('/manifests')
def manifests():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('manifests.html')

@app.route('/api/v1/manifests')
def api_manifests():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    sort_col = request.args.get('sort', 'cargo_id')
    order = request.args.get('order', 'asc')
    
    # Security Check
    if not waf_filter(sort_col) or not waf_filter(order):
        return jsonify({"error": "Malicious input detected"}), 400

    # Vulnerable Query Construction
    # The WAF blocks spaces, but SQLite allows /**/ for spaces
    # The sort parameter is directly injected into the ORDER BY clause
    query = f"SELECT cargo_id, weight, destination, status FROM manifests ORDER BY {sort_col} {order}"
    
    try:
        conn = get_db_connection()
        results = conn.execute(query).fetchall()
        conn.close()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database error"}), 500

@app.route('/contractors')
def contractors():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    contractors = conn.execute("SELECT * FROM contractors").fetchall()
    conn.close()
    return render_template('contractors.html', contractors=contractors)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)