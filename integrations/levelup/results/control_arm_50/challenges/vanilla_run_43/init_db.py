import sqlite3
import os

def init():
    db_path = '/tmp/vanguard_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Components table
    cursor.execute('''
    CREATE TABLE components (
        part_id INTEGER PRIMARY KEY,
        part_name TEXT NOT NULL,
        serial_number TEXT NOT NULL,
        stock_level INTEGER
    )
    ''')

    # Obfuscated Flag table
    cursor.execute('''
    CREATE TABLE audit_system_config (
        id INTEGER PRIMARY KEY,
        config_key TEXT NOT NULL,
        config_value TEXT NOT NULL
    )
    ''')

    # Seed Data
    parts = [
        (1001, 'Titanium Turbine Blade', 'SN-XB921', 45),
        (1002, 'Hydraulic Actuator', 'SN-HA112', 12),
        (1003, 'Avionics Logic Board', 'SN-LB004', 89),
        (1004, 'Composite Fuselage Panel', 'SN-CF440', 5),
        (1005, 'Fuel Injection Nozzle', 'SN-FN771', 120)
    ]
    cursor.executemany('INSERT INTO components VALUES (?,?,?,?)', parts)

    # Insert Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute('INSERT INTO audit_system_config (config_key, config_value) VALUES (?,?)', ('system_master_key', flag))
    except:
        pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()