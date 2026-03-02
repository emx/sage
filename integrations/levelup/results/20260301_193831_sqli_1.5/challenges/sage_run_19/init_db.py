import sqlite3
import os

def init():
    db_path = '/tmp/velostratus.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Realistic tables
    c.execute('CREATE TABLE drones (id INTEGER PRIMARY KEY, drone_id TEXT, model TEXT, battery_level INTEGER, status TEXT)')
    c.execute('CREATE TABLE flight_logs (id INTEGER PRIMARY KEY, drone_id TEXT, origin TEXT, destination TEXT, start_time TEXT, duration INTEGER)')
    c.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER, warehouse TEXT)')
    c.execute('CREATE TABLE pilots (id INTEGER PRIMARY KEY, name TEXT, license_id TEXT, certification_level TEXT)')
    c.execute('CREATE TABLE maintenance_records (id INTEGER PRIMARY KEY, drone_id TEXT, description TEXT, date TEXT, cost REAL)')

    # Obfuscated table for flag
    c.execute('CREATE TABLE v_internal_dispatch_metadata (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')

    # Seed data
    drones = [('DRN-902', 'Stratus-X1', 98, 'Active'), ('DRN-441', 'HeavyLift-V2', 45, 'Charging'), ('DRN-112', 'Swift-S3', 72, 'Active')]
    c.executemany('INSERT INTO drones (drone_id, model, battery_level, status) VALUES (?,?,?,?)', drones)

    maint = [
        ('DRN-902', 'Rotor blade replacement', '2023-10-01', 450.00),
        ('DRN-441', 'Sensor calibration', '2023-10-05', 120.50),
        ('DRN-112', 'Battery stress test', '2023-10-12', 85.00)
    ]
    c.executemany('INSERT INTO maintenance_records (drone_id, description, date, cost) VALUES (?,?,?,?)', maint)

    # Insert flag from file
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute('INSERT INTO v_internal_dispatch_metadata (config_key, config_value) VALUES (?, ?)', ('master_dispatch_key', flag))
    c.execute('INSERT INTO v_internal_dispatch_metadata (config_key, config_value) VALUES (?, ?)', ('api_endpoint_v2', 'https://telemetry-internal.velostratus.local/v2'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()