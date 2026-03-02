import sqlite3
import json
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
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

@app.before_request
def waf_filter():
    # Realistic but flawed WAF: Checks raw request data for forbidden SQL keywords
    if request.is_json:
        raw_data = request.get_data().decode().upper()
        forbidden = ['SELECT', 'UNION', 'WHERE', 'AND', 'OR', 'LIKE', 'UPDATE', 'DELETE', 'INSERT', 'SLEEP', '--']
        for word in forbidden:
            if word in raw_data:
                return jsonify({"error": "Security violation detected", "detail": f"Keyword '{word}' is prohibited."}), 403

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple authentication for demo purposes
        if username == 'guest' and password == 'guest':
            session['user'] = 'guest'
            session['role'] = 'Logistics Coordinator'
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/shipments')
def shipments():
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    items = db.execute('SELECT * FROM containers LIMIT 10').fetchall()
    return render_template('shipments.html', items=items)

@app.route('/shipment/<int:item_id>')
def shipment_detail(item_id):
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    item = db.execute('SELECT * FROM containers WHERE id = ?', (item_id,)).fetchone()
    if not item: return "Shipment not found", 404
    return render_template('shipment_detail.html', item=item)

@app.route('/verify')
def verify_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('verify.html')

@app.route('/api/v1/manifest/verify', methods=['POST'])
def api_verify():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if not data or 'serial' not in data:
        return jsonify({"error": "Missing serial number"}), 400
    
    serial = data.get('serial')
    db = get_db()
    
    # VULNERABILITY: Raw string formatting in SQL query
    # The WAF is bypassed because request.get_json() decodes Unicode escapes 
    # AFTER the @app.before_request WAF checked the raw byte stream.
    query = f"SELECT id FROM containers WHERE serial_no = '{serial}'"
    
    try:
        result = db.execute(query).fetchone()
        if result:
            return jsonify({"status": "verified", "manifest_id": result['id']}), 200
        else:
            return jsonify({"status": "not_found", "message": "No matching manifest in active registry."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": "Internal processing error"}), 500

@app.route('/inventory')
def inventory():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('inventory.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)