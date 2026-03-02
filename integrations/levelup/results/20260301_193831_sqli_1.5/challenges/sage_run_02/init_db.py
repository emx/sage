import sqlite3
import os

def init():
    # Ensure the DB is in /tmp for the read-only FS requirement
    db_path = '/tmp/velosync.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE fleet_logs (id INTEGER PRIMARY KEY, vehicle_id TEXT, driver TEXT, location TEXT, cargo TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE system_vault (id INTEGER PRIMARY KEY, prop_key TEXT, prop_val TEXT)''')

    # Seed users
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'redacted_super_secret_9921', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'viewer')")

    # Seed logs
    logs = [
        ('VS-101', 'James Miller', '40.7128 N, 74.0060 W', 'Consumer Electronics', '2023-10-01 08:30:00'),
        ('VS-101', 'James Miller', '34.0522 N, 118.2437 W', 'Consumer Electronics', '2023-10-02 14:20:00'),
        ('VS-101', 'James Miller', '41.8781 N, 87.6298 W', 'Industrial Parts', '2023-10-03 09:15:00'),
        ('VS-202', 'Sarah Chen', '25.7617 N, 80.1918 W', 'Medical Supplies', '2023-10-01 11:00:00')
    ]
    cursor.executemany("INSERT INTO fleet_logs (vehicle_id, driver, location, cargo, timestamp) VALUES (?, ?, ?, ?, ?)", logs)

    # Seed flag into the vault (obfuscated name)
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_vault (prop_key, prop_val) VALUES ('sys.integrity.checksum', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO system_vault (prop_key, prop_val) VALUES ('sys.integrity.checksum', 'LEVELUP{PLACEHOLDER_FLAG}')")

    conn.commit()
    conn.close()
    # Set permissions so ctfuser can read it
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()