import sqlite3
import os

def init():
    db_path = '/tmp/orbitstream.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Realistic Tables
    cursor.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cargo_id TEXT,
        origin TEXT,
        destination TEXT,
        weight INTEGER,
        status TEXT
    )''')

    cursor.execute('''CREATE TABLE access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        action TEXT,
        status TEXT
    )''')

    cursor.execute('''CREATE TABLE system_parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT,
        value TEXT
    )''')

    # Seed Data
    manifests = [
        ('OSL-9921', 'Lunar Station V', 'Mars Hangar 4', 12500, 'In Transit'),
        ('OSL-1024', 'Earth Orbital Platform', 'ISS Replacement Node', 4500, 'Docked'),
        ('OSL-5512', 'Belt Miner X', 'Earth Orbital Platform', 89000, 'Processing'),
        ('OSL-8831', 'Mars Hangar 1', 'Titan Outpost', 2200, 'Scheduled')
    ]
    cursor.executemany('INSERT INTO manifests (cargo_id, origin, destination, weight, status) VALUES (?,?,?,?,?)', manifests)

    logs = [
        ('DEV-99', '2024-05-10 08:00:01', 'UPLINK_START', 'SUCCESS'),
        ('DEV-99', '2024-05-10 09:15:22', 'DATA_TRANSFER', 'SUCCESS'),
        ('DEV-99', '2024-05-10 10:30:45', 'UPLINK_END', 'SUCCESS'),
        ('DEV-001', '2024-05-11 11:20:00', 'HEARTBEAT', 'OK'),
        ('DEV-001', '2024-05-11 12:20:00', 'HEARTBEAT', 'OK')
    ]
    cursor.executemany('INSERT INTO access_logs (device_id, timestamp, action, status) VALUES (?,?,?,?)', logs)

    # Flag Isolation: Read flag from /flag.txt and insert into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute('INSERT INTO system_parameters (key, value) VALUES (?, ?)', ('core_uplink_auth_token', flag))
    except Exception as e:
        print(f"Error reading flag: {e}")

    cursor.execute('INSERT INTO system_parameters (key, value) VALUES (?, ?)', ('maintenance_mode', 'false'))
    cursor.execute('INSERT INTO system_parameters (key, value) VALUES (?, ?)', ('region_code', 'US-EAST-ORBIT-1'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()