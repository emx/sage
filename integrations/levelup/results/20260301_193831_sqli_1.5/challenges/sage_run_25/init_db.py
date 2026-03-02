import sqlite3
import os

def init():
    # Database path in /tmp for read-only filesystem compatibility
    db_path = '/tmp/verdant_path.db'
    
    # Remove existing db if any
    if os.path.exists(db_path): os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
        CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
        CREATE TABLE regions (id INTEGER PRIMARY KEY, name TEXT, climate TEXT);
        CREATE TABLE crop_yields (id INTEGER PRIMARY KEY, region_id INTEGER, crop_type TEXT, yield_amount REAL, year INTEGER);
        CREATE TABLE sensors (id INTEGER PRIMARY KEY, sensor_tag TEXT, type TEXT, reading REAL, unit TEXT, region_name TEXT, timestamp TEXT);
        CREATE TABLE system_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT);
    ''')

    # Seed data
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'p@ssw0rd123_very_long_and_secure', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'viewer')")

    regions = [(1, 'Central Plains', 'Temperate'), (2, 'Southern Delta', 'Humid'), (3, 'Coastal Ridge', 'Maritime')]
    cursor.executemany("INSERT INTO regions VALUES (?,?,?)", regions)

    yields = [
        (1, 1, 'Corn', 185.2, 2021), (2, 1, 'Wheat', 72.5, 2021), (3, 1, 'Corn', 192.1, 2022), (4, 1, 'Soybeans', 55.4, 2022),
        (5, 2, 'Rice', 142.8, 2021), (6, 2, 'Cotton', 1.2, 2021), (7, 2, 'Rice', 138.5, 2022), (8, 3, 'Grapes', 12.4, 2022)
    ]
    cursor.executemany("INSERT INTO crop_yields VALUES (?,?,?,?,?)", yields)

    sensors = [
        ('SN-1001', 'Soil Moisture', 42.5, '%', 'Central Plains', '2024-05-12 10:00:01'),
        ('SN-1002', 'Soil pH', 6.8, 'pH', 'Central Plains', '2024-05-12 10:05:00'),
        ('SN-2001', 'Temperature', 28.4, 'C', 'Southern Delta', '2024-05-12 09:55:20')
    ]
    for i, s in enumerate(sensors):
        cursor.execute("INSERT INTO sensors (id, sensor_tag, type, reading, unit, region_name, timestamp) VALUES (?,?,?,?,?,?,?)", (i+1, *s))

    # Import flag from /flag.txt
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('integrity_verification_token', ?)", (flag,))
    except Exception as e:
        print(f"Error reading flag: {e}")

    cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('api_version', '1.4.2-stable')")
    cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('maintenance_mode', 'false')")

    conn.commit()
    conn.close()
    print("Database initialized at /tmp/verdant_path.db")

if __name__ == '__main__':
    init()