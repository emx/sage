import sqlite3
import os

def init():
    # Database path must be in /tmp/ for runtime write access
    db_path = '/tmp/vortex.db'
    
    # Ensure the directory exists (though /tmp always does)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, container_id TEXT, origin TEXT, destination TEXT, weight INTEGER, status TEXT)''')
    # Obfuscated table for the flag
    cursor.execute('''CREATE TABLE vortex_system_settings (id INTEGER PRIMARY KEY, setting_key TEXT, setting_value TEXT)''')

    # Seed users
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'RedactedPassword2024!', 'administrator')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'viewer')")

    # Seed shipments
    manifests = [
        ('VV-8821-A', 'Singapore', 'Rotterdam', 12500, 'IN_TRANSIT'),
        ('VV-1092-B', 'Shanghai', 'Long Beach', 22400, 'ARRIVED'),
        ('VV-5542-C', 'Hamburg', 'Dubai', 18900, 'PENDING'),
        ('VV-9910-D', 'Tokyo', 'London', 15600, 'IN_TRANSIT'),
        ('VV-3321-E', 'Mumbai', 'New York', 21000, 'ARRIVED')
    ]
    cursor.executemany("INSERT INTO shipments (container_id, origin, destination, weight, status) VALUES (?, ?, ?, ?, ?)", manifests)

    # Insert the flag from the root-only file
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO vortex_system_settings (setting_key, setting_value) VALUES ('internal_auth_token', ?)", (flag,))
    except Exception as e:
        print(f"Error reading flag: {e}")

    conn.commit()
    conn.close()
    
    # Ensure ctfuser can read the database at runtime
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()