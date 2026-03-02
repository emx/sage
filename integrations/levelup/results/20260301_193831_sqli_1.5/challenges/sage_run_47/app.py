import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def security_filter(payload):
    # Simulated WAF blocking common SQLi keywords
    blacklist = ['UNION', 'OR', '--', '/*', 'SLEEP', 'BENCHMARK', 'HEX']
    if any(word in payload.upper() for word in blacklist):
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Mock login for demo purposes
        session['user'] = request.form.get('username')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/silos')
def silos():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    silos = conn.execute('SELECT * FROM silos').fetchall()
    conn.close()
    return render_template('silos.html', silos=silos)

@app.route('/reports/view/<int:id>')
def view_report(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    report = conn.execute('SELECT * FROM shipments WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('report.html', report=report)

@app.route('/api/shipments/search')
def api_search():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    sort_by = request.args.get('sort', 'id')
    
    if not security_filter(sort_by):
        return jsonify({'error': 'Security violation detected'}), 400

    try:
        conn = get_db_connection()
        # VULNERABILITY: String interpolation in ORDER BY clause
        query = f"SELECT id, origin, destination, status FROM shipments ORDER BY {sort_by}"
        shipments = conn.execute(query).fetchall()
        conn.close()
        return jsonify([dict(row) for row in shipments])
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/admin/audit')
def admin_audit():
    # Red herring and hint for the internal_telemetry table
    return "Under Maintenance: Automated audit logs are currently being archived to internal_telemetry table.", 503

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)