import sqlite3
import os

def init():
    db_path = '/tmp/aetherflow.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        display_name TEXT,
        region TEXT
    )''')

    # Shipments table
    cursor.execute('''
    CREATE TABLE shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_id TEXT NOT NULL,
        origin TEXT,
        destination TEXT,
        status TEXT,
        region TEXT
    )''')

    # Obfuscated metadata table for the flag
    cursor.execute('''
    CREATE TABLE system_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_name TEXT,
        config_value TEXT
    )''')

    # Fleet metrics table
    cursor.execute('''
    CREATE TABLE fleet_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        fuel INTEGER,
        temp INTEGER
    )''')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password, display_name, region) VALUES ('coordinator', 'AetherFlow2024!', 'Primary Coordinator', 'NORTH-01')")
    
    shipments = [
        ('AF-9921', 'New York, NY', 'Philadelphia, PA', 'In Transit', 'NORTH-01'),
        ('AF-4412', 'Boston, MA', 'Hartford, CT', 'Delivered', 'NORTH-01'),
        ('AF-1092', 'Chicago, IL', 'Detroit, MI', 'Delayed', 'MIDWEST-05'),
        ('AF-3321', 'Seattle, WA', 'Portland, OR', 'Pending', 'WEST-02')
    ]
    cursor.executemany("INSERT INTO shipments (tracking_id, origin, destination, status, region) VALUES (?, ?, ?, ?, ?)", shipments)

    fleet = [
        ('TRUCK-001', 85, 92),
        ('TRUCK-009', 42, 95),
        ('VAN-202', 100, 88)
    ]
    cursor.executemany("INSERT INTO fleet_metrics (vehicle_id, fuel, temp) VALUES (?, ?, ?)", fleet)

    # Read flag from /flag.txt and insert into metadata
    try:
        with open('/flag.txt', 'r') as f:
            flag_content = f.read().strip()
        cursor.execute("INSERT INTO system_metadata (config_name, config_value) VALUES ('master_flag', ?)", (flag_content,))
        cursor.execute("INSERT INTO system_metadata (config_name, config_value) VALUES ('db_version', 'v4.2.1')")
    except Exception as e:
        print(f"Error reading flag: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()