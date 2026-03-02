import sqlite3
import random
import os

def init():
    db_path = '/app/velonexus.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table 1: Shipments
    cursor.execute('''
    CREATE TABLE shipments (
        id INTEGER PRIMARY KEY,
        container_id TEXT,
        origin TEXT,
        destination TEXT,
        status TEXT
    )''')

    origins = ['Shanghai', 'Singapore', 'Rotterdam', 'Los Angeles', 'Hamburg', 'Dubai', 'Busan', 'Antwerp']
    destinations = ['New York', 'London', 'Tokyo', 'Sydney', 'Mumbai', 'Santos', 'Felixstowe', 'Piraeus']
    statuses = ['In Transit', 'Pending Clearance', 'Departed', 'Arrived', 'Delayed', 'Processing']

    for i in range(1, 101):
        cursor.execute('INSERT INTO shipments (container_id, origin, destination, status) VALUES (?, ?, ?, ?)',
            (f'VNXU{random.randint(100000, 999999)}', random.choice(origins), random.choice(destinations), random.choice(statuses)))

    # Table 2: Audit Logs (Obfuscated Flag Storage)
    cursor.execute('''
    CREATE TABLE system_audit_log (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        action_type TEXT,
        action_metadata TEXT
    )''')

    cursor.execute("INSERT INTO system_audit_log (action_type, action_metadata) VALUES ('SYSTEM_INIT', 'Service started successfully')")
    cursor.execute("INSERT INTO system_audit_log (action_type, action_metadata) VALUES ('USER_LOGIN', 'Admin user accessed management console from 127.0.0.1')")
    
    # The Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_audit_log (action_type, action_metadata) VALUES ('ENCRYPTION_KEY_ROTATION', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO system_audit_log (action_type, action_metadata) VALUES ('ENCRYPTION_KEY_ROTATION', 'LEVELUP{PLACEHOLDER_FLAG}')")

    for i in range(50):
        cursor.execute("INSERT INTO system_audit_log (action_type, action_metadata) VALUES (?, ?)", 
            (random.choice(['ACCESS_LOG', 'DB_CLEANUP', 'HEALTH_CHECK']), f'System event ID {random.randint(1000,9999)}'))

    # Table 3: Staff (Red Herring)
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT)')
    cursor.execute("INSERT INTO users (username, password_hash) VALUES ('admin', 'pbkdf2:sha256:600000$rest_of_hash_is_useless_here')")

    conn.commit()
    conn.close()
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()