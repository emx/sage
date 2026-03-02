import sqlite3
import re
import os
from flask import Flask, request, render_template, redirect, url_for, session, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(payload):
    # Harder WAF: Detects keywords followed by spaces/tabs or common comments
    forbidden = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'FROM', 'LIMIT', 'JOIN', 'SLEEP']
    pattern = r'(' + '|'.join(forbidden) + r')(\s+|\/\*|--)'
    if re.search(pattern, payload, re.IGNORECASE):
        return False
    if "--" in payload: # Strictly block standard comments
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
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests LIMIT 5').fetchall()
    return render_template('dashboard.html', manifests=manifests)

@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        subject = request.form.get('subject', '')
        description = request.form.get('description', '')
        
        if not waf_check(subject):
            return render_template('tickets.html', error="Security Trigger: Malicious pattern detected in subject line.")
        
        db.execute('INSERT INTO tickets (user_id, subject, description) VALUES (?, ?, ?)',
                   (session['user_id'], subject, description))
        db.commit()
        return redirect(url_for('tickets', message="Ticket submitted successfully."))

    user_tickets = db.execute('SELECT * FROM tickets WHERE user_id = ?', (session['user_id'],)).fetchall()
    return render_template('tickets.html', tickets=user_tickets, message=request.args.get('message'))

@app.route('/tickets/view/<int:ticket_id>')
def view_ticket(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    ticket = db.execute('SELECT * FROM tickets WHERE id = ? AND user_id = ?', (ticket_id, session['user_id'])).fetchone()
    if not ticket:
        return redirect(url_for('dashboard'))
    
    # SECOND-ORDER SQL INJECTION VULNERABILITY
    # The 'subject' from the database is concatenated directly into the query.
    # The WAF was only applied at the insertion stage.
    try:
        query = f"SELECT * FROM audit_logs WHERE log_entry LIKE '%{ticket['subject']}%'"
        logs = db.execute(query).fetchall()
        has_logs = len(logs) > 0
    except Exception:
        has_logs = False

    return render_template('ticket_view.html', ticket=ticket, has_logs=has_logs)

@app.route('/api/v1/health')
def health():
    return {"status": "healthy", "service": "vanguard-logistics-core"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)