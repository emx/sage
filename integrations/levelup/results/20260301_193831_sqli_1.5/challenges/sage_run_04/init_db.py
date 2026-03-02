import sqlite3
import os

def init():
    db_path = '/tmp/veridian.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE drones (id INTEGER PRIMARY KEY, serial TEXT, model TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE maintenance_logs (id INTEGER PRIMARY KEY, drone_id TEXT, technician_id TEXT, description TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE site_configuration (id INTEGER PRIMARY KEY, config_name TEXT, config_value TEXT)''')

    # Seed users
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', '" + os.urandom(16).hex() + "', 'administrator')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'coordinator')")

    # Seed drones
    drones = [
        ('VK-7742', 'Stratus-X1', 'Active'),
        ('VK-1109', 'Carrier-V9', 'Maintenance'),
        ('VK-5521', 'Stratus-X1', 'Active'),
        ('VK-9902', 'Scout-S2', 'Decommissioned')
    ]
    cursor.executemany("INSERT INTO drones (serial, model, status) VALUES (?, ?, ?)", drones)

    # Seed maintenance logs
    logs = [
        ('VK-7742', 'TECH-04', 'Battery recalibration', '2023-10-01 09:00:00'),
        ('VK-1109', 'TECH-12', 'Rotor blade replacement', '2023-10-05 14:20:00'),
        ('VK-5521', 'TECH-04', 'Firmware update v2.4', '2023-10-10 11:15:00'),
        ('VK-9902', 'TECH-07', 'End of life inspection', '2023-10-12 16:45:00')
    ]
    cursor.executemany("INSERT INTO maintenance_logs (drone_id, technician_id, description, timestamp) VALUES (?, ?, ?, ?)", logs)

    # Seed obfuscated flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO site_configuration (config_name, config_value) VALUES ('master_access_token', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO site_configuration (config_name, config_value) VALUES ('master_access_token', 'FLAG_NOT_FOUND')")

    cursor.execute("INSERT INTO site_configuration (config_name, config_value) VALUES ('api_timeout', '30')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()