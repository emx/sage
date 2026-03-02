import sqlite3
import re
from flask import Flask, render_template, request, jsonify, g
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def security_filter(payload):
    # WAF: Block spaces, common SQL comments, and logical operators
    forbidden = [" ", "--", "#", " OR ", " AND ", "WAITFOR", "SLEEP"]
    for item in forbidden:
        if item.upper() in payload.upper():
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    stats = db.execute("SELECT COUNT(*) as count, region FROM vessels GROUP BY region").fetchall()
    return render_template('dashboard.html', stats=stats)

@app.route('/vessels')
def vessels():
    db = get_db()
    vessel_list = db.execute("SELECT * FROM vessels").fetchall()
    return render_template('vessels.html', vessels=vessel_list)

@app.route('/harvests')
def harvests():
    return render_template('harvests.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/v1/harvest/history')
def harvest_history():
    sort_column = request.args.get('sort', 'harvest_date')
    
    if not security_filter(sort_column):
        return jsonify({"error": "Security violation detected by VKM-Guard"}), 403

    db = get_db()
    try:
        # Vulnerable ORDER BY injection
        query = f"SELECT h.*, v.vessel_name FROM harvests h JOIN vessels v ON h.vessel_id = v.id ORDER BY {sort_column} ASC"
        results = db.execute(query).fetchall()
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, message="Resource Not Found"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)