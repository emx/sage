import sqlite3
import os

def init():
    # Database path in /tmp for read-only FS
    db_path = '/tmp/nebula_logistics.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create standard tables
    cursor.execute('''
    CREATE TABLE containers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_no TEXT NOT NULL,
        contents TEXT,
        origin TEXT,
        destination TEXT,
        status TEXT
    )''')

    # Create obfuscated table for secrets
    cursor.execute('''
    CREATE TABLE system_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registry_key TEXT NOT NULL,
        registry_value TEXT NOT NULL
    )''')

    # Seed realistic data
    shipments = [
        ('NS-1001', '7nm Logic Processors', 'Hsinchu, TW', 'San Jose, US', 'In Transit'),
        ('NS-1002', 'High-Bandwidth Memory', 'Seoul, KR', 'Austin, US', 'Processing'),
        ('NS-1003', 'EUV Photolithography Masks', 'Veldhoven, NL', 'Phoenix, US', 'Arrived'),
        ('NS-1004', 'Rare Earth Substrates', 'Shanghai, CN', 'Munich, DE', 'In Transit'),
        ('NS-1005', 'Gallium Nitride Wafers', 'Tokyo, JP', 'Dresden, DE', 'Delayed')
    ]
    cursor.executemany('INSERT INTO containers (serial_no, contents, origin, destination, status) VALUES (?,?,?,?,?)', shipments)

    # Read flag and insert into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_registry (registry_key, registry_value) VALUES ('core_system_access_token', ?)", (flag,))
    except Exception as e:
        print(f"Error reading flag: {e}")

    # Add red herring registry entries
    cursor.execute("INSERT INTO system_registry (registry_key, registry_value) VALUES ('api_version', 'v2.4.1-stable')")
    cursor.execute("INSERT INTO system_registry (registry_key, registry_value) VALUES ('region_code', 'US-WEST-2')")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init()