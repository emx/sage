import sqlite3
import os

def init():
    db_path = '/tmp/skyworks.db'
    if os.path.exists(db_path): os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tables
    cursor.execute('''CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,
        part_name TEXT,
        category TEXT,
        description TEXT,
        stock_level INTEGER
    )''')

    cursor.execute('''CREATE TABLE warehouses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        location TEXT,
        manager TEXT
    )''')

    cursor.execute('''CREATE TABLE procurement_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_id INTEGER,
        requester_email TEXT,
        warehouse_ref TEXT
    )''')

    cursor.execute('''CREATE TABLE system_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_name TEXT,
        key_value TEXT
    )''')

    # Seed Data
    parts = [
        ('AS-901', 'Titanium Turbine Blade', 'Engine Components', 'Specially forged for high-temperature durability.', 45),
        ('AS-442', 'Avionics Control Unit', 'Electronics', 'Flight control computer for A320 series.', 12),
        ('AS-102', 'Hydraulic Actuator', 'Landing Gear', 'Standard landing gear deployment system.', 30),
        ('AS-550', 'Carbon Fiber Winglet', 'Airframe', 'Fuel-saving wingtip extension.', 8)
    ]
    cursor.executemany('INSERT INTO inventory (sku, part_name, category, description, stock_level) VALUES (?,?,?,?,?)', parts)

    warehouses = [
        ('WH-001', 'London Heathrow Distribution', 'Alice Henderson'),
        ('WH-002', 'Singapore Changi Hub', 'Marcus Chen'),
        ('WH-003', 'Toulouse Assembly Point', 'Jean Dupont'),
        ('WH-004', 'Seattle Manufacturing Center', 'Sarah Miller')
    ]
    cursor.executemany('INSERT INTO warehouses (code, location, manager) VALUES (?,?,?)', warehouses)

    # Add a system setting (Flag is added in Dockerfile)
    cursor.execute("INSERT INTO system_config (key_name, key_value) VALUES ('app_version', '2.4.1')")
    cursor.execute("INSERT INTO system_config (key_name, key_value) VALUES ('maint_mode', 'false')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()