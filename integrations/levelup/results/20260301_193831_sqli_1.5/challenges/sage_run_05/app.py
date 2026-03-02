import sqlite3
import re
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vql_internal_secure_key_8821'
DATABASE = '/tmp/logistics.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def waf_filter(payload):
    # Realistic WAF: blocks common SQL keywords only if they are standalone words
    # This allows bypassing using parentheses like SELECT(1)FROM(table)
    blacklist = ["SELECT", "UNION", "WHERE", "JOIN", "OR", "AND", "SLEEP", "BENCHMARK", "GROUP", "HAVING"]
    for word in blacklist:
        if re.search(rf"\b{word}\b", payload.upper()):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

@app.route('/couriers')
def couriers():
    db = get_db()
    couriers = db.execute('SELECT * FROM couriers').fetchall()
    return render_template('couriers.html', couriers=couriers)

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/login')
def login():
    return render_template('login.html', error="Admin login is restricted to internal VPC endpoints only.")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('about.html', contact=True)

@app.route('/api/v1/inventory/report')
def inventory_report():
    sort_by = request.args.get('sort', 'id')
    
    if not waf_filter(sort_by):
        return jsonify({"error": "Security Alert: Malicious SQL patterns detected."}), 403

    try:
        db = get_db()
        # Vulnerable ORDER BY injection
        query = f"SELECT id, item_name, quantity, warehouse_id FROM warehouse_inventory ORDER BY {sort_by}"
        items = db.execute(query).fetchall()
        return jsonify([dict(row) for row in items])
    except Exception as e:
        return jsonify({"error": "Database Error", "details": str(e)}), 500

if __name__ == '__main__':
    # Ensure DB exists at runtime
    if not os.path.exists(DATABASE):
        import shutil
        if os.path.exists('/app/logistics.db'):
            shutil.copy('/app/logistics.db', DATABASE)
    app.run(host='0.0.0.0', port=5000)