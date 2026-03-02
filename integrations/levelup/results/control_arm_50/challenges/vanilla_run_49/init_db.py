import sqlite3
import os

def init():
    db_path = '/tmp/aetherflow.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables
    cursor.execute('''CREATE TABLE components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_number TEXT,
        name TEXT,
        category TEXT,
        location TEXT
    )''')
    
    cursor.execute('''CREATE TABLE maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component_id INTEGER,
        technician TEXT,
        status TEXT,
        notes TEXT
    )''')
    
    cursor.execute('''CREATE TABLE internal_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_name TEXT,
        config_value TEXT
    )''')
    
    # Seed Data
    parts = [
        ('SENS-001', 'High-Gain IR Sensor', 'Optical', 'Warehouse-Alpha'),
        ('PROP-99', 'Ion Thruster Array', 'Propulsion', 'Warehouse-Beta'),
        ('BATT-42', 'Li-Ion Power Cell', 'Energy', 'Warehouse-Gamma')
    ]
    cursor.executemany('INSERT INTO components (part_number, name, category, location) VALUES (?,?,?,?)', parts)
    
    logs = [
        (1, 'Eng. Marcus', 'Certified', 'Lenses calibrated to 0.001 micron'),
        (2, 'Eng. Sarah', 'Pending', 'Fuel valve pressure test required'),
    ]
    cursor.executemany('INSERT INTO maintenance_logs (component_id, technician, status, notes) VALUES (?,?,?,?)', logs)
    
    # Read flag and hide it
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{LOCAL_TEST_FLAG}"
        
    cursor.execute('INSERT INTO internal_configs (config_name, config_value) VALUES (?,?)', ('master_access_key', flag))
    cursor.execute('INSERT INTO internal_configs (config_name, config_value) VALUES (?,?)', ('api_version', 'v2.4.1-stable'))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()