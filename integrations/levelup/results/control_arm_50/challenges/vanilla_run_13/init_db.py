import sqlite3
import os

def init():
    db_path = '/tmp/aetherflow.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', '7df4237f8888b11c', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'viewer')")

    # Cargo Pods
    cursor.execute('CREATE TABLE pods (id INTEGER PRIMARY KEY, pod_serial TEXT, cargo_type TEXT, origin TEXT, destination TEXT, status TEXT)')
    pods_data = [
        ('AF-901', 'Medical Supplies', 'Berlin', 'Munich', 'In-Transit'),
        ('AF-402', 'Electronics', 'Shanghai', 'Tokyo', 'Arrived'),
        ('AF-118', 'Perishables', 'New York', 'Boston', 'Pending'),
        ('AF-552', 'Industrial Parts', 'London', 'Paris', 'In-Transit')
    ]
    cursor.executemany("INSERT INTO pods (pod_serial, cargo_type, origin, destination, status) VALUES (?,?,?,?,?)", pods_data)

    # Diagnostics Table
    cursor.execute('CREATE TABLE diagnostics (id INTEGER PRIMARY KEY, pod_id INTEGER, sensor_type TEXT, value TEXT, reading_time TEXT)')
    diag_data = [
        (1, 'Temperature', '4.2C', '2024-05-20 10:00'),
        (1, 'Vibration', '0.02g', '2024-05-20 10:00'),
        (2, 'Temperature', '18.5C', '2024-05-20 11:30'),
        (3, 'Battery', '94%', '2024-05-20 09:15')
    ]
    cursor.executemany("INSERT INTO diagnostics (pod_id, sensor_type, value, reading_time) VALUES (?,?,?,?)", diag_data)

    # Obfuscated Flag Table
    cursor.execute('CREATE TABLE system_vault (id INTEGER PRIMARY KEY, vault_key TEXT, vault_value TEXT)')
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{MOCK_FLAG_FOR_TESTING}"
    
    cursor.execute("INSERT INTO system_vault (vault_key, vault_value) VALUES ('root_access_canary', ?)", (flag,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()