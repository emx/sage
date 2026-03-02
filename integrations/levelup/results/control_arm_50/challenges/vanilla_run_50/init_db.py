import sqlite3
import os

def init():
    # Ensure DB is in /tmp for write access on read-only fs
    db_path = '/tmp/aetheris.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cargo_name TEXT,
        contractor TEXT,
        destination TEXT,
        priority TEXT
    )''')

    cursor.execute('''CREATE TABLE tracking_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id TEXT UNIQUE,
        status TEXT,
        last_location TEXT
    )''')

    cursor.execute('''CREATE TABLE contractors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mission_type TEXT,
        email TEXT
    )''')

    # Obfuscated table for flag
    cursor.execute('''CREATE TABLE logistics_meta (
        meta_id INTEGER PRIMARY KEY AUTOINCREMENT,
        meta_key TEXT,
        meta_value TEXT
    )''')

    # Seed Data
    cursor.execute("INSERT INTO manifests (cargo_name, contractor, destination, priority) VALUES ('StarLink-X9', 'SpaceTech Inc', 'Orbit LEO-4', 'High')")
    cursor.execute("INSERT INTO manifests (cargo_name, contractor, destination, priority) VALUES ('DeepSpace Probe', 'NASA/JPL', 'Hohmann Transfer', 'Critical')")
    cursor.execute("INSERT INTO manifests (cargo_name, contractor, destination, priority) VALUES ('Resupply-22', 'Orbital Dynamics', 'ISS Docking Node 2', 'Medium')")

    cursor.execute("INSERT INTO tracking_logs (tracking_id, status, last_location) VALUES ('T-772-B', 'IN_TRANSIT', 'Geostationary-Ring-Alpha')")
    cursor.execute("INSERT INTO tracking_logs (tracking_id, status, last_location) VALUES ('T-104-X', 'DOCKED', 'ISS-Gateway')")

    cursor.execute("INSERT INTO contractors (name, mission_type, email) VALUES ('Apex Launch Systems', 'Heavy Lift', 'ops@apex.aero')")
    cursor.execute("INSERT INTO contractors (name, mission_type, email) VALUES ('Nebula Orbital', 'Payload Delivery', 'contact@nebula.space')")

    # Insert Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO logistics_meta (meta_key, meta_value) VALUES ('orbital_encryption_key', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO logistics_meta (meta_key, meta_value) VALUES ('orbital_encryption_key', 'LEVELUP{DUMMY_FLAG}')")

    cursor.execute("INSERT INTO logistics_meta (meta_key, meta_value) VALUES ('system_version', 'v1.4.2-legacy')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()