import os
import sqlite3
import shutil
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "73rr4_5ync_53cr37_k3y_2024"
DB_PATH = "/tmp/terrasync.db"
ORIG_DB = "/app/terrasync.db"

def get_db_connection():
    # Ensure DB is in writable /tmp/
    if not os.path.exists(DB_PATH):
        shutil.copy(ORIG_DB, DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def simple_waf(data):
    # A realistic 'naive' WAF that blocks keywords followed by spaces
    blacklist = ["SELECT ", "UNION ", "WHERE ", "OR ", "AND ", "--", "INSERT ", "UPDATE ", "DELETE "]
    if not data:
        return True
    for word in blacklist:
        if word in data.upper():
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
        if username == "agronomist" and password == "terra-sync-2024":
            session['user'] = username
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    plots = conn.execute("SELECT * FROM soil_plots LIMIT 10").fetchall()
    conn.close()
    return render_template('dashboard.html', plots=plots)

@app.route('/plot/<int:plot_id>')
def plot_detail(plot_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    plot = conn.execute("SELECT * FROM soil_plots WHERE id = ?", (plot_id,)).fetchone()
    metrics = conn.execute("SELECT * FROM chemistry_metrics WHERE plot_id = ?", (plot_id,)).fetchall()
    conn.close()
    return render_template('plot_detail.html', plot=plot, metrics=metrics)

@app.route('/logs')
def logs():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    sort_by = request.args.get('sort', 'timestamp')
    
    # Security Check
    if not simple_waf(sort_by):
        return "Security Alert: Malicious SQL patterns detected.", 403

    conn = get_db_connection()
    # VULNERABILITY: String concatenation in ORDER BY clause
    query = f"SELECT id, timestamp, event, user FROM system_logs ORDER BY {sort_by} DESC"
    try:
        logs = conn.execute(query).fetchall()
    except Exception as e:
        return f"Database Error: {str(e)}", 500
    finally:
        conn.close()
    
    return render_template('logs.html', logs=logs)

@app.route('/api/v1/status')
def status():
    return {"status": "operational", "database": "connected", "version": "2.4.1-stable"}

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)