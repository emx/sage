import sqlite3
import os

def init():
    db_path = '/tmp/aerospace.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE propulsion_units (id INTEGER PRIMARY KEY, serial_no TEXT, model TEXT, facility_id TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE vault_metadata (id INTEGER PRIMARY KEY, config_name TEXT, config_value TEXT)''')
    
    # Insert users
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'VK_740_SuperSecret_2024', 'administrator')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('tech_alicia', 'propulsion_pro_99', 'technician')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest1234', 'guest')")
    
    # Insert units
    units = [
        ('VK-740-A', 'Kestrel-X1', 'FAC-01', 'Active'),
        ('VK-740-B', 'Kestrel-X1', 'FAC-01', 'Maintenance'),
        ('VK-920-X', 'Eagle-Prop', 'FAC-02', 'Active'),
        ('VK-101-C', 'Kestrel-Lite', 'FAC-03', 'Active'),
        ('VK-202-D', 'Kestrel-Lite', 'FAC-01', 'Active')
    ]
    cursor.executemany("INSERT INTO propulsion_units (serial_no, model, facility_id, status) VALUES (?, ?, ?, ?)", units)
    
    # Insert flag into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO vault_metadata (config_name, config_value) VALUES ('maintenance_access_key', ?)", (flag,))
    except Exception:
        cursor.execute("INSERT INTO vault_metadata (config_name, config_value) VALUES ('maintenance_access_key', 'LEVELUP{MOCK_FLAG_FOR_TESTING}')")

    # Extra data for noise
    cursor.execute("INSERT INTO vault_metadata (config_name, config_value) VALUES ('api_version', '1.4.2-stable')")
    cursor.execute("INSERT INTO vault_metadata (config_name, config_value) VALUES ('facility_sync_interval', '300')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()