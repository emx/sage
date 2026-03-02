import sqlite3
import re
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import config

app = Flask(__name__)
app.config.from_object(config)

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(data):
    # Hardened WAF: Blocks common keywords and standard spaces
    blocked = ['select', 'union', 'where', 'or', ' ', '--', 'sleep', 'benchmark']
    if any(keyword in data.lower() for keyword in blocked):
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
        # Simple authentication for demonstration
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

@app.route('/sensors')
def sensors():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('sensors.html')

@app.route('/api/v1/sensors/telemetry', methods=['POST'])
def telemetry_api():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    enrichment = data.get('enrichment', '')
    
    if not waf_filter(enrichment):
        return jsonify({"error": "Security Violation: Malicious Keyword Detected"}), 403

    try:
        db = get_db()
        # The vulnerability: Unsafe concatenation of 'enrichment' into the query
        # Purpose: Allows agronomists to join sensor data with regions or crop types
        query = f"SELECT sensor_readings.* FROM sensor_readings {enrichment} LIMIT 10"
        cursor = db.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": "Query Error"}), 500

@app.route('/api/v1/docs')
def api_docs():
    return render_template('api_docs.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)