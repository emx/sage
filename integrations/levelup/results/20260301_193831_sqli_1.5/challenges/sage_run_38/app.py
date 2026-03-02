import os
import sqlite3
import re
from flask import Flask, request, render_template, jsonify, g

app = Flask(__name__)
app.config.from_object('config')
DATABASE = '/tmp/velolink.db'

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

def veloguard_filter(payload):
    # VeloGuard Middleware: Protection against common SQLi patterns
    # Blocks spaces, UNION, OR, and comments
    blacklist = ['UNION', 'OR', '--', ' ', '/*', '*/']
    if any(item in payload.upper() for item in blacklist):
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

@app.route('/vessels')
def vessels():
    db = get_db()
    vessels = db.execute('SELECT * FROM vessels').fetchall()
    return render_template('vessels.html', vessels=vessels)

@app.route('/vessel/<int:vessel_id>')
def vessel_detail(vessel_id):
    return render_template('vessel_detail.html', vessel_id=vessel_id)

@app.route('/customs/login')
def login():
    return render_template('login.html')

@app.route('/api/v1/status')
def status():
    return jsonify({"status": "operational", "node": "LON-01", "load": "14%"})

@app.route('/api/v1/vessel/details')
def api_vessel_details():
    vessel_id = request.args.get('id', '')
    
    if not vessel_id:
        return jsonify({"error": "Missing vessel ID"}), 400

    if veloguard_filter(vessel_id):
        return jsonify({"error": "Security violation: VeloGuard blocked suspicious payload"}), 403

    db = get_db()
    try:
        # Vulnerable query: direct concatenation
        query = f"SELECT id, name, flag_state, vessel_type, status FROM vessels WHERE id = {vessel_id}"
        result = db.execute(query).fetchone()
        
        if result:
            return jsonify(dict(result))
        else:
            return jsonify({"error": "Vessel not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "debug": str(e) if app.debug else "none"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)