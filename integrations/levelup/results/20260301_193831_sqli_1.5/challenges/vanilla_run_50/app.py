import sqlite3
import re
import os
from flask import Flask, request, render_template, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = '/tmp/aetheris.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def security_gate(payload):
    # Realistic 'naive' WAF that looks for lowercase patterns and spaces
    # It misses case variation like 'sElEcT' and bypasses like comments
    blacklist = ['union', 'select', 'where', 'and', 'or', '--', ' ']
    for item in blacklist:
        if item in payload:
            return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifests')
def manifest_list():
    db = get_db()
    manifests = db.execute('SELECT * FROM manifests').fetchall()
    return render_template('manifests.html', manifests=manifests)

@app.route('/manifest/view/<int:id>')
def manifest_detail(id):
    db = get_db()
    manifest = db.execute('SELECT * FROM manifests WHERE id = ?', (id,)).fetchone()
    if not manifest:
        return "Manifest not found", 404
    return render_template('manifest_detail.html', manifest=manifest)

@app.route('/track')
def tracking_ui():
    return render_template('track.html')

@app.route('/api/v1/track/status')
def api_tracking():
    tid = request.args.get('tid', '')
    
    if not tid:
        return jsonify({"status": "error", "message": "Missing Tracking ID"}), 400

    if not security_gate(tid):
        return jsonify({"status": "error", "message": "Security violation detected"}), 403

    try:
        db = get_db()
        # Vulnerable Sink: Intentional f-string injection
        query = f"SELECT status, last_location FROM tracking_logs WHERE tracking_id = '{tid}'"
        result = db.execute(query).fetchone()

        if result:
            return jsonify({
                "status": "success",
                "data": {
                    "tracking_id": tid,
                    "status": result['status'],
                    "location": result['last_location']
                }
            })
        else:
            return jsonify({"status": "error", "message": "No logs found for this ID"}), 404
    except Exception as e:
        # Obfuscated error to prevent direct debug info but indicate SQL error
        return jsonify({"status": "error", "message": "System fault in tracking engine"}), 500

@app.route('/contractors')
def contractors():
    db = get_db()
    partners = db.execute('SELECT * FROM contractors').fetchall()
    return render_template('contractors.html', partners=partners)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "Employee Single-Sign-On is currently offline. Please use the Orbital VPN.", 503
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)