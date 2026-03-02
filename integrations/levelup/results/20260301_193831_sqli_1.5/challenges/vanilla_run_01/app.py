import os
import sqlite3
import re
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, abort
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def logistics_waf(payload):
    # A realistic, but flawed WAF that looks for space-delimited keywords
    forbidden = ['SELECT ', 'UNION ', 'FROM ', 'WHERE ', 'LIMIT ', 'OFFSET ', 'OR ', 'AND ']
    if not payload:
        return True
    
    check_val = payload.upper()
    for word in forbidden:
        if word in check_val:
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
        # Simple demo auth
        if (username == 'guest' and password == 'guest') or (username == 'admin' and password == 'VeloAdmin2024!'):
            session['user'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/manifests')
def manifests_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('manifests.html')

@app.route('/api/v1/manifests')
def api_manifests():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    sort_column = request.args.get('sort', 'id')
    
    # The Vulnerability: Direct interpolation into ORDER BY
    # Combined with the WAF check
    if not logistics_waf(sort_column):
        return abort(403, description="Logistics-WAF: Potential SQL Injection Detected")

    try:
        db = get_db()
        query = f"SELECT id, tracking_id, destination, weight, status FROM shipments ORDER BY {sort_column} ASC"
        rows = db.execute(query).fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": "Database Error", "details": str(e)}), 500

@app.route('/vehicles')
def vehicles():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    vehicles = db.execute("SELECT * FROM vehicles").fetchall()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user=session['user'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)