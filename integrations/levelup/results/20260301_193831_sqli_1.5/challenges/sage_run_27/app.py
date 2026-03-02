import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, g
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

def security_filter(payload):
    # Mimic a WAF that looks for space-separated SQL keywords
    if not payload: return True
    blacklist = ['SELECT ', 'UNION ', 'FROM ', 'WHERE ', 'OR ', 'AND ', '--', '/*']
    for item in blacklist:
        if item in payload.upper():
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
            return redirect('/dashboard')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/shipments')
def shipments():
    if 'user' not in session:
        return redirect('/login')
    
    db = get_db()
    sort_field = request.headers.get('X-Sort-Field', 'shipment_id')
    
    # The vulnerability: Sort field is directly interpolated if it passes the WAF
    if not security_filter(sort_field):
        return "Security Alert: Malicious activity detected.", 403

    query = f"SELECT * FROM shipments ORDER BY {sort_field} ASC"
    try:
        shipments = db.execute(query).fetchall()
    except Exception as e:
        return f"Internal Database Error", 500
        
    return render_template('shipments.html', shipments=shipments)

@app.route('/shipment/<int:id>')
def shipment_detail(id):
    if 'user' not in session:
        return redirect('/login')
    db = get_db()
    shipment = db.execute("SELECT * FROM shipments WHERE id = ?", (id,)).fetchone()
    driver = db.execute("SELECT * FROM drivers WHERE id = ?", (shipment['driver_id'],)).fetchone()
    return render_template('details.html', shipment=shipment, driver=driver)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/status')
def status():
    return {"status": "operational", "version": "2.4.1-stable"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)