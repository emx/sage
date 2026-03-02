import sqlite3
import os

def init():
    db_path = '/tmp/aetheris_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manifest_id TEXT,
        origin TEXT,
        destination TEXT,
        cargo_type TEXT,
        weight INTEGER
    )''')

    cursor.execute('''CREATE TABLE fleet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        model TEXT,
        status TEXT,
        last_location TEXT
    )''')

    cursor.execute('''CREATE TABLE system_integrity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT,
        config_value TEXT
    )''')

    manifests = [
        ('M-9021', 'London, UK', 'New York, USA', 'Electronics', 4500),
        ('M-4412', 'Tokyo, JP', 'Berlin, DE', 'Automotive Parts', 12000),
        ('M-1120', 'Shanghai, CN', 'Sydney, AU', 'Textiles', 8000),
        ('M-5591', 'Dubai, UAE', 'Paris, FR', 'Luxury Goods', 500)
    ]
    cursor.executemany('INSERT INTO manifests (manifest_id, origin, destination, cargo_type, weight) VALUES (?,?,?,?,?)', manifests)

    fleet = [
        ('Atlas-01', 'Heavy Duty Semi', 'active', '40.7128° N, 74.0060° W'),
        ('Boreas-04', 'Medium Cargo Van', 'maintenance', '51.5074° N, 0.1278° W'),
        ('Zephyr-09', 'Light Delivery Truck', 'active', '35.6762° N, 139.6503° E')
    ]
    cursor.executemany('INSERT INTO fleet (name, model, status, last_location) VALUES (?,?,?,?)', fleet)

    try:
        with open('/flag.txt', 'r') as f:
            flag_content = f.read().strip()
    except:
        flag_content = "LEVELUP{LOCAL_TEST_FLAG}"

    cursor.execute('INSERT INTO system_integrity (config_key, config_value) VALUES (?,?)', ('emergency_backup_key', flag_content))
    cursor.execute('INSERT INTO system_integrity (config_key, config_value) VALUES (?,?)', ('api_version', '1.4.2-stable'))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()