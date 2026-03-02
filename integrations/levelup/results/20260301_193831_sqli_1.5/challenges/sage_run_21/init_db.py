import sqlite3
import os

DB_PATH = '/tmp/aetheria_telematics.db'

def init():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )''')
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('technician', 'drone_safety_2024', 'staff')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', '5up3r_53cur3_v4ul7_2024', 'admin')")

    # Drones Table
    cursor.execute('''CREATE TABLE drones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number TEXT,
        model TEXT,
        status TEXT,
        battery_level INTEGER
    )''')
    drones = [
        ('SN-772-X', 'Eagle Eye V2', 'Active', 88),
        ('SN-109-B', 'Cargo Lifter', 'Maintenance', 12),
        ('SN-332-Q', 'Eagle Eye V2', 'Active', 95),
        ('SN-901-Z', 'Surveyor Pro', 'Charging', 45)
    ]
    cursor.executemany("INSERT INTO drones (serial_number, model, status, battery_level) VALUES (?,?,?,?)", drones)

    # Maintenance Logs Table
    cursor.execute('''CREATE TABLE maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drone_id INTEGER,
        technician_id TEXT,
        log_entry TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    logs = [
        (1, 'TECH_01', 'Replaced rotor blade assembly on motor 3.', '2024-10-01 09:15:00'),
        (2, 'TECH_04', 'Battery cell balancing completed.', '2024-10-01 11:20:00'),
        (1, 'TECH_01', 'Firmware updated to v4.5.12.', '2024-10-02 14:00:00'),
        (3, 'TECH_02', 'Ultrasonic sensor calibration performed.', '2024-10-03 08:45:00')
    ]
    cursor.executemany("INSERT INTO maintenance_logs (drone_id, technician_id, log_entry, timestamp) VALUES (?,?,?,?)", logs)

    # Internal Config (Flag Table)
    cursor.execute('''CREATE TABLE internal_system_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT,
        setting_value TEXT
    )''')
    
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    cursor.execute("INSERT INTO internal_system_data (setting_name, setting_value) VALUES ('emergency_access_key', ?)", (flag,))
    cursor.execute("INSERT INTO internal_system_data (setting_name, setting_value) VALUES ('telemetry_encryption_level', 'High')")
    cursor.execute("INSERT INTO internal_system_data (setting_name, setting_value) VALUES ('arctic_relay_address', '10.55.21.4')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()