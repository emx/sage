import sqlite3
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "v3lo_gr33n_5up3r_53cr3t_k3y_2024"
DATABASE = "/tmp/velogreen.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf_filter(input_str):
    # Realistic mistake: case-sensitive filtering on a case-insensitive database
    blacklisted = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'INSERT', 'DELETE', 'UPDATE', '--', '/*', 'HEX']
    for word in blacklisted:
        if word in input_str:
            return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = 'guest_agronomist'
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    plots = db.execute('SELECT * FROM plots').fetchall()
    return render_template('dashboard.html', plots=plots)

@app.route('/plot/<int:plot_id>')
def plot_detail(plot_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    db = get_db()
    plot = db.execute('SELECT * FROM plots WHERE id = ?', (plot_id,)).fetchone()
    readings = db.execute('SELECT * FROM sensor_readings WHERE plot_id = ? ORDER BY timestamp DESC LIMIT 10', (plot_id,)).fetchall()
    return render_template('plot_detail.html', plot=plot, readings=readings)

@app.route('/diagnostics')
def diagnostics():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('diagnostics.html')

@app.route('/api/v1/diagnostics/logs')
def api_diagnostics():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403
    
    sort_by = request.args.get('sort', 'timestamp')
    
    if waf_filter(sort_by):
        return jsonify({"error": "Security alert: Malicious input detected"}), 400

    try:
        db = get_db()
        # Vulnerable ORDER BY injection
        query = f"SELECT id, sensor_id, temperature, status, timestamp FROM sensor_logs ORDER BY {sort_by} ASC"
        logs = db.execute(query).fetchall()
        return jsonify([dict(log) for log in logs])
    except Exception as e:
        return jsonify({"error": "Database error occurred"}), 500

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /diagnostics\nDisallow: /api/v1/diagnostics/logs"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)