import sqlite3
import re
from flask import Flask, render_template, request, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DATABASE = '/tmp/veloscore.db'

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

def waf_filter(s):
    if not s:
        return True
    # Realistic WAF: Blocks UNION, OR, spaces, and comments
    # Players must use tabs (%09), newlines (%0A), or parentheses for separation
    blacklist = [r'UNION', r'OR', r'\s+', r'--', r'\/\*']
    for pattern in blacklist:
        if re.search(pattern, s, re.IGNORECASE):
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    sort_by = request.args.get('sort', 'part_name')
    
    if not waf_filter(sort_by):
        return render_template('error.html', message="Security Alert: Malicious input detected in sorting parameter."), 403

    db = get_db()
    try:
        # Vulnerable ORDER BY injection
        query = f"SELECT id, part_name, sku, category, quantity FROM inventory ORDER BY {sort_by}"
        parts = db.execute(query).fetchall()
    except Exception as e:
        return render_template('error.html', message="Database Error: Sorting criteria invalid."), 500

    return render_template('catalog.html', parts=parts, current_sort=sort_by)

@app.route('/parts/<int:part_id>')
def details(part_id):
    db = get_db()
    part = db.execute('SELECT * FROM inventory WHERE id = ?', (part_id,)).fetchone()
    if part is None:
        return "Part not found", 404
    return render_template('details.html', part=part)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)