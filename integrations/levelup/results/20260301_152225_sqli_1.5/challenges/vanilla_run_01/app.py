import os
import sqlite3
from flask import Flask, render_template, request, jsonify, g
from config import DATABASE, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Advanced Logic Filter (ALF) Middleware
def alf_filter(input_str):
    if not input_str:
        return True
    blacklist = ['UNION', 'OR', 'AND', '--', '/*', '  ']
    # The filter is case-insensitive
    check_str = input_str.upper()
    
    for word in blacklist:
        if word in check_str:
            return False
    
    # Strict check for SELECT with a space
    if 'SELECT ' in check_str:
        return False
        
    # Block standard spaces to force more creative bypasses
    if ' ' in input_str:
        return False
        
    return True

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/api/v1/cargo/search')
def cargo_search():
    search = request.args.get('q', '')
    sort = request.args.get('sort', 'item_name')

    # Apply ALF protection to the sort parameter
    if not alf_filter(sort):
        return jsonify({"error": "Security Alert: Malicious pattern detected in sort parameter."}), 403

    db = get_db()
    try:
        # Vulnerable ORDER BY injection point
        query = f"SELECT id, item_name, weight, warehouse_id FROM inventory WHERE item_name LIKE ? ORDER BY {sort}"
        cursor = db.execute(query, (f"%{search}%",))
        results = [dict(row) for row in cursor.fetchall()]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": "Database error occurred during processing."}), 500

@app.route('/manifests')
def manifests():
    # Red herring endpoint - looks like it needs login
    return render_template('manifests.html', msg="Unauthorized: Manifest access restricted to Warehouse Managers.")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content="404 Not Found"), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)