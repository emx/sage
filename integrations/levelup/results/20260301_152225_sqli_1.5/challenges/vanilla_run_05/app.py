import os
import sqlite3
import re
import time
from flask import Flask, render_template, request, g

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
DATABASE = '/tmp/auraflow.db'

class SecurityShield:
    def __init__(self):
        # Expanded blacklist to block common logic flow and keywords
        self.blacklist = ['SELECT', 'UNION', 'FROM', 'WHERE', 'AND', 'OR', 'LIKE', 'LIMIT', 'OFFSET', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'SLEEP']
        # Create a case-insensitive regex pattern for all blacklisted words
        self.pattern = re.compile('|'.join(self.blacklist), re.IGNORECASE)

    def sanitize(self, value):
        if not value:
            return value
        # The calibrator noted case-sensitivity was a flaw. 
        # Now we use a case-insensitive replacement to attempt hardening.
        # However, a single-pass replacement can still be bypassed with nested keywords (e.g., SELSELECTECT)
        sanitized = self.pattern.sub('', value)
        return sanitized

shield = SecurityShield()

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

@app.route('/catalog')
def catalog():
    db = get_db()
    clips = db.execute('SELECT * FROM media_clips LIMIT 12').fetchall()
    return render_template('catalog.html', clips=clips)

@app.route('/clip/<int:clip_id>')
def clip_details(clip_id):
    db = get_db()
    clip = db.execute('SELECT * FROM media_clips WHERE id = ?', (clip_id,)).fetchone()
    if not clip:
        return "Clip not found", 404
    return render_template('details.html', clip=clip)

@app.route('/license', methods=['GET', 'POST'])
def license():
    if request.method == 'POST':
        return render_template('license.html', success=True)
    return render_template('license.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/archive/explorer')
def explorer():
    # Artificial delay to make blind-based extraction significantly more time-consuming
    time.sleep(0.2)
    
    sort_val = request.args.get('sort', 'id')
    
    # Multi-layer defense: normalization + single-pass regex filtering
    sanitized_sort = shield.sanitize(sort_val)
    
    # The vulnerability remains: Unsafe interpolation in ORDER BY
    query = f"SELECT id, title, category, broadcast_year FROM media_clips ORDER BY {sanitized_sort}"
    
    db = get_db()
    try:
        clips = db.execute(query).fetchall()
    except Exception:
        # REMOVED RAW ERROR MESSAGES: Error feedback is now suppressed to prevent easy extraction.
        # Users must now rely on boolean or time-based blind injection techniques.
        return render_template('explorer.html', error="An internal database error occurred while processing the sort request.")
        
    return render_template('explorer.html', clips=clips, current_sort=sort_val)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)