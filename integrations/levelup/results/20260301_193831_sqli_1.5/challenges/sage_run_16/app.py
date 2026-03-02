import sqlite3
import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, abort
from functools import wraps

app = Flask(__name__)
app.secret_key = "aetheris_logistics_secret_key_2024"
DATABASE = '/tmp/aetheris.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def waf(payload):
    if not payload:
        return True
    # Hardened filter: No spaces, common SQL keywords, or comments
    forbidden = [" ", "UNION", "WHERE", "OR", "AND", "--", "/*", "SLEEP"]
    for word in forbidden:
        if word in payload.upper():
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

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/shipments')
@login_required
def shipments():
    db = get_db()
    shipments = db.execute('SELECT * FROM shipments').fetchall()
    return render_template('shipments.html', shipments=shipments)

@app.route('/shipment/<int:shipment_id>')
@login_required
def shipment_detail(shipment_id):
    db = get_db()
    shipment = db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)).fetchone()
    manifests = db.execute('SELECT * FROM manifests WHERE shipment_id = ?', (shipment_id,)).fetchall()
    if not shipment:
        abort(404)
    return render_template('shipment_detail.html', shipment=shipment, manifests=manifests)

@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/v1/reports/legacy_manifest')
@login_required
def legacy_manifest():
    order_by = request.args.get('order_by', 'id')
    
    # SECURITY CHECK
    if not waf(order_by):
        return jsonify({"status": "error", "message": "Malicious input detected"}), 400
    
    try:
        db = get_db()
        # VULNERABILITY: Direct string interpolation into ORDER BY clause
        query = f"SELECT id, cargo_type, weight, signature FROM manifests ORDER BY {order_by}"
        results = db.execute(query).fetchall()
        return jsonify([dict(r) for r in results])
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)