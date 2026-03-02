import sqlite3
import os

DB_PATH = '/tmp/verdant_pulse.db'

def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Main shipment table
    cursor.execute('''
        CREATE TABLE shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    # Silo management table
    cursor.execute('''
        CREATE TABLE silos (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            capacity REAL,
            grain_type TEXT
        )
    ''')

    # Obfuscated table for flag isolation
    cursor.execute('''
        CREATE TABLE internal_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT NOT NULL,
            entry TEXT NOT NULL
        )
    ''')

    # Seed Data
    shipments = [
        ('Fairview Farm', 'Central Hub', 'In Transit'),
        ('Oak Valley', 'North Processing', 'Delivered'),
        ('River Delta', 'South Silo', 'Pending'),
        ('Mountain Peak', 'West Depot', 'Loading'),
        ('Green Plains', 'Central Hub', 'Scheduled')
    ]
    cursor.executemany('INSERT INTO shipments (origin, destination, status) VALUES (?, ?, ?)', shipments)

    silos = [
        (101, 'Silo Alpha', 50000.0, 'Wheat'),
        (102, 'Silo Beta', 75000.0, 'Corn'),
        (103, 'Silo Gamma', 40000.0, 'Soybeans')
    ]
    cursor.executemany('INSERT INTO silos VALUES (?, ?, ?, ?)', silos)

    # Read flag and insert
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute('INSERT INTO internal_telemetry (tag, entry) VALUES (?, ?)', ('SYSTEM_FLAG_KEY', flag))
    except Exception:
        cursor.execute('INSERT INTO internal_telemetry (tag, entry) VALUES (?, ?)', ('SYSTEM_FLAG_KEY', 'DEBUG_FLAG_LOCAL'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()