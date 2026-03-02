import sqlite3
import os

def init():
    db_path = '/tmp/aetherlogix.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Realistic tables
    c.execute('CREATE TABLE components (id INTEGER PRIMARY KEY, serial_no TEXT, name TEXT, manufacturer TEXT, weight REAL)')
    c.execute('CREATE TABLE launch_schedules (id INTEGER PRIMARY KEY, mission_name TEXT, launch_date TEXT, pad_location TEXT, payload_description TEXT)')
    c.execute('CREATE TABLE personnel (id INTEGER PRIMARY KEY, name TEXT, role TEXT, location TEXT)')
    c.execute('CREATE TABLE telemetry (sensor_id INTEGER PRIMARY KEY, sensor_name TEXT, reading TEXT, status TEXT)')
    
    # Obfuscated table for flag
    c.execute('CREATE TABLE legacy_telemetry_meta (id INTEGER PRIMARY KEY, key_id TEXT, meta_value TEXT)')

    # Seed Data
    c.execute("INSERT INTO components (serial_no, name, manufacturer, weight) VALUES ('AX-101', 'Cryo-Fuel Pump', 'DynoSystems', 450.5)")
    c.execute("INSERT INTO components (serial_no, name, manufacturer, weight) VALUES ('AX-105', 'Star-Tracker v4', 'OpticVoid', 12.2)")
    c.execute("INSERT INTO launch_schedules (mission_name, launch_date, pad_location, payload_description) VALUES ('Aether-1', '2024-12-15', 'Kourou Pad A', 'Comm-Sat 12')")
    c.execute("INSERT INTO personnel (name, role, location) VALUES ('Alice Vance', 'Chief Engineer', 'Station Alpha')")
    c.execute("INSERT INTO telemetry (sensor_id, sensor_name, reading, status) VALUES (1, 'Main Engine Temp', '452K', 'OPTIMAL')")
    c.execute("INSERT INTO telemetry (sensor_id, sensor_name, reading, status) VALUES (2, 'Fuel Level', '98%', 'NOMINAL')")
    
    # Insert Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO legacy_telemetry_meta (key_id, meta_value) VALUES ('SYSTEM_ROOT_SECRET', ?)", (flag,))
    except:
        c.execute("INSERT INTO legacy_telemetry_meta (key_id, meta_value) VALUES ('SYSTEM_ROOT_SECRET', 'LEVELUP{local_test_flag}')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()