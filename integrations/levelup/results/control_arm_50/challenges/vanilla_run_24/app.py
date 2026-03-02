import os
import sqlite3
import re
from flask import Flask, request, render_template, make_response, redirect, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Aetheria-Super-Secret-Key-2024'
DATABASE = '/tmp/skyworks.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def waf_check(payload):
    if not payload:
        return True
    # AetheriaWAF v1.0 - Detects common SQL injection patterns
    blacklist = [r'UNION', r'--', r'\/\*', r'OR 1=1', r'SLEEP']
    for pattern in blacklist:
        if re.search(pattern, str(payload), re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    db = get_db()
    parts = db.execute('SELECT * FROM inventory').fetchall()
    return render_template('inventory.html', parts=parts)

@app.route('/inventory/<int:part_id>')
def detail(part_id):
    db = get_db()
    part = db.execute('SELECT * FROM inventory WHERE id = ?', (part_id,)).fetchone()
    if not part:
        return "Part not found", 404
    return render_template('detail.html', part=part)

@app.route('/request-quote', methods=['GET', 'POST'])
def request_quote():
    if request.method == 'POST':
        part_id = request.form.get('part_id')
        email = request.form.get('email')
        # Vulnerable Header
        warehouse_ref = request.headers.get('X-Warehouse-Ref', 'WH-001')

        if not waf_check(warehouse_ref):
            return "Security Alert: Malicious activity detected by AetheriaWAF", 403

        db = get_db()
        db.execute('INSERT INTO procurement_requests (part_id, requester_email, warehouse_ref) VALUES (?, ?, ?)',
                   (part_id, email, warehouse_ref))
        db.commit()
        return render_template('request.html', success=True)
    
    part_id = request.args.get('part_id')
    return render_template('request.html', part_id=part_id)

@app.route('/admin/audit-logs')
def audit_logs():
    # Authentication check
    if request.cookies.get('staff_access') != '1':
        return "Unauthorized: Staff access only. Please ensure staff_access cookie is set.", 401

    db = get_db()
    logs = db.execute('SELECT r.id, i.part_name, r.requester_email, r.warehouse_ref FROM procurement_requests r JOIN inventory i ON r.part_id = i.id').fetchall()
    
    audit_data = []
    for log in logs:
        ref = log['warehouse_ref']
        try:
            # SECOND-ORDER VULNERABILITY: Stored header value is used directly in query
            query = f"SELECT location FROM warehouses WHERE code = '{ref}'"
            warehouse = db.execute(query).fetchone()
            status = "Valid Warehouse" if warehouse else "Unknown Warehouse"
            location = warehouse['location'] if warehouse else "N/A"
        except Exception as e:
            status = "Audit Error"
            location = "ERROR"
            
        audit_data.append({
            'id': log['id'],
            'part': log['part_name'],
            'email': log['requester_email'],
            'ref': ref,
            'status': status,
            'location': location
        })
    
    return render_template('audit.html', logs=audit_data)

@app.route('/api/v1/health')
def health():
    return {"status": "online", "version": "2.4.1"}

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /admin/audit-logs", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)