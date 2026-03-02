import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def waf_check(payload):
    blacklist = ['union', '--', '/*', 'offset', 'drop', 'update', 'delete']
    for word in blacklist:
        if word in payload.lower():
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
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/tracking')
def tracking():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    shipments = conn.execute('SELECT * FROM shipments LIMIT 20').fetchall()
    conn.close()
    return render_template('tracking.html', shipments=shipments)

@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user_reports = conn.execute('SELECT * FROM user_reports WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('reports.html', reports=user_reports)

@app.route('/reports/new', methods=['GET', 'POST'])
def create_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('report_name')
        sort_by = request.form.get('sort_by')
        
        if not waf_check(sort_by):
            flash('Security Warning: Prohibited keywords detected in sorting parameters.')
            return render_template('reports_new.html')

        conn = get_db_connection()
        conn.execute('INSERT INTO user_reports (user_id, report_name, sort_column) VALUES (?, ?, ?)',
                     (session['user_id'], name, sort_by))
        conn.commit()
        conn.close()
        return redirect(url_for('reports'))
        
    return render_template('reports_new.html')

@app.route('/reports/view/<int:report_id>')
def view_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    report = conn.execute('SELECT * FROM user_reports WHERE id = ? AND user_id = ?', (report_id, session['user_id'])).fetchone()
    
    if not report:
        conn.close()
        return "Report not found", 404

    # Vulnerable Second-Order SQL Injection in ORDER BY
    try:
        query = f"SELECT * FROM shipments ORDER BY {report['sort_column']}"
        shipments = conn.execute(query).fetchall()
    except Exception as e:
        # Friendly error to keep the realism
        return f"Internal Database Error: The report sorting criteria '{report['sort_column']}' is invalid.", 500
    
    conn.close()
    return render_template('report_view.html', shipments=shipments, report_name=report['report_name'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)