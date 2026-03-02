import sqlite3
import os

def init():
    db_path = '/tmp/aetherbound.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Users table
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'CelestialAdmin2024!@', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('dispatcher_alpha', 'Payload123', 'user')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'viewer')")

    # Manifests table
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, tracking_id TEXT, payload_name TEXT, destination TEXT, weight INTEGER, status TEXT)')
    manifests = [
        ('AB-1001', 'O2 Scrubbers', 'ISS-Zarya', 450, 'In Transit'),
        ('AB-1024', 'Xenon Fuel', 'Gateway-Station', 1200, 'Processing'),
        ('AB-2045', 'Medical Supplies', 'Luna-Base-1', 150, 'Departed'),
        ('AB-3091', 'Solar Array B', 'Mars-Orbit-Relay', 3200, 'Awaiting Launch'),
        ('AB-0092', 'Cryo-Chamber', 'DeepSpace-Proxima', 5600, 'Pre-load')
    ]
    c.executemany('INSERT INTO manifests (tracking_id, payload_name, destination, weight, status) VALUES (?,?,?,?,?)', manifests)

    # Obfuscated Flag Table
    c.execute('CREATE TABLE system_node_diagnostics (id INTEGER PRIMARY KEY, node_id TEXT, diag_payload TEXT)')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag_val = f.read().strip()
    except:
        flag_val = 'LEVELUP{FLAG_NOT_FOUND_REBUILD_CONTAINER}'

    c.execute("INSERT INTO system_node_diagnostics (node_id, diag_payload) VALUES ('ORD-MANIFEST-01', ?)", (flag_val,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()