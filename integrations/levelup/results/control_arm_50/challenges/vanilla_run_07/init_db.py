import sqlite3
import os

def init():
    conn = sqlite3.connect('/tmp/aetherlink.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT)')
    cursor.execute('CREATE TABLE shipment_records (shipment_id TEXT, destination TEXT, status TEXT)')
    cursor.execute('CREATE TABLE telemetry_logs (id INTEGER PRIMARY KEY, shipment_id TEXT, sensor_type TEXT, reading TEXT, timestamp TEXT)')
    cursor.execute('CREATE TABLE internal_assets (id INTEGER PRIMARY KEY, asset_name TEXT, asset_value TEXT)')

    # Seed Shipments
    shipments = [
        ('AE-9921', 'Singapore', 'In Transit'),
        ('AE-1022', 'Rotterdam', 'Delivered'),
        ('AE-4431', 'Dubai', 'Processing'),
        ('AE-5520', 'New York', 'Delayed')
    ]
    cursor.executemany('INSERT INTO shipment_records (shipment_id, destination, status) VALUES (?, ?, ?)', shipments)

    # Seed Telemetry (Sorted values for blind SQLi logic)
    telemetry = [
        (1, 'AE-1022', 'Temp', '2.4C', '2024-05-01 10:00'),
        (2, 'AE-9921', 'GPS', '1.33, 103.8', '2024-05-01 11:00'),
        (3, 'AE-4431', 'Humidity', '45%', '2024-05-01 12:00')
    ]
    cursor.executemany('INSERT INTO telemetry_logs (id, shipment_id, sensor_type, reading, timestamp) VALUES (?, ?, ?, ?, ?)', telemetry)

    # Read flag and insert into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{DUMMY_FLAG}"
    
    cursor.execute('INSERT INTO internal_assets (asset_name, asset_value) VALUES (?, ?)', ('SYSTEM_MASTER_KEY', flag))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()