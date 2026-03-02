import sqlite3
import os

def init():
    db_path = '/tmp/vanguard_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE inventory (id INTEGER PRIMARY KEY, item_name TEXT, serial_no TEXT, location TEXT)''')
    cursor.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_id TEXT, material TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, timestamp TEXT, action TEXT, details TEXT)''')
    cursor.execute('''CREATE TABLE vanguard_config (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')

    # Seed data
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'REDACTED_NOT_THE_FLAG', 'administrator')")
    cursor.execute("INSERT INTO users VALUES (2, 'guest', 'guest123', 'viewer')")

    inventory_data = [
        ('Ion Thruster Core', 'SN-992-X', 'Warehouse A-12'),
        ('Solar Array Panel', 'SN-102-B', 'Warehouse B-05'),
        ('Xenon Fuel Tank', 'SN-443-K', 'Warehouse A-01'),
        ('Guidance Computer', 'SN-881-Z', 'Warehouse C-09')
    ]
    cursor.executemany("INSERT INTO inventory (item_name, serial_no, location) VALUES (?, ?, ?)", inventory_data)

    shipments_data = [
        ('VG-882199', 'Liquid Oxygen', 'In Transit'),
        ('VG-110293', 'Hypergolic Fuel', 'Stored'),
        ('VG-554211', 'Hydrazine Component', 'Delivered')
    ]
    cursor.executemany("INSERT INTO shipments (tracking_id, material, status) VALUES (?, ?, ?)", shipments_data)

    audit_data = [
        ('2023-10-24 08:30:11', 'LOGIN', 'User guest logged in from 10.0.4.5'),
        ('2023-10-24 09:15:22', 'VIEW', 'Inventory list accessed by guest'),
        ('2023-10-24 10:05:45', 'LOGOUT', 'User guest logged out'),
        ('2023-10-24 11:00:01', 'SYSTEM', 'Automated backup of manifest database completed')
    ]
    cursor.executemany("INSERT INTO audit_logs (timestamp, action, details) VALUES (?, ?, ?)", audit_data)

    # Read flag and insert into config table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO vanguard_config (config_key, config_value) VALUES ('master_access_token', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO vanguard_config (config_key, config_value) VALUES ('master_access_token', 'FLAG_NOT_FOUND_IN_INIT')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()