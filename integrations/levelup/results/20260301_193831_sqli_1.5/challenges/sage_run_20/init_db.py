import sqlite3
import os

def init():
    db_path = "vanguard.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE containers (
        id INTEGER PRIMARY KEY,
        container_id TEXT,
        vessel TEXT,
        destination TEXT,
        status TEXT
    )''')

    cursor.execute('''CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY,
        event_type TEXT,
        operator_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE site_settings (
        id INTEGER PRIMARY KEY,
        key TEXT,
        value TEXT
    )''')

    # Seed Data
    containers = [
        ('VG-1029', 'SS Oceanic', 'Rotterdam', 'Cleared'),
        ('VG-7721', 'Deep-Sea Voyager', 'Singapore', 'In Transit'),
        ('VG-4490', 'Arctic Pioneer', 'Oslo', 'Held in Customs'),
        ('VG-8812', 'SS Oceanic', 'New York', 'Cleared')
    ]
    cursor.executemany('INSERT INTO containers (container_id, vessel, destination, status) VALUES (?,?,?,?)', containers)

    logs = [
        ('MANIFEST_VIEW', 1),
        ('LOGIN_SUCCESS', 1),
        ('CERT_UPLOAD', 2),
        ('MANIFEST_UPDATE', 1)
    ]
    cursor.executemany('INSERT INTO audit_logs (event_type, operator_id) VALUES (?,?)', logs)

    # Read flag and insert into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{MOCK_FLAG_FOR_TESTING}"

    cursor.execute('INSERT INTO site_settings (key, value) VALUES (?, ?)', ('site_name', 'Vanguard Deep-Sea Logistics'))
    cursor.execute('INSERT INTO site_settings (key, value) VALUES (?, ?)', ('master_security_hash', flag))
    cursor.execute('INSERT INTO site_settings (key, value) VALUES (?, ?)', ('api_version', '2.4.1-stable'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()