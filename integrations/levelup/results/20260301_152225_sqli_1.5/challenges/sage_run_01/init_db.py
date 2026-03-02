import sqlite3
import os

def init():
    db_path = '/tmp/veridiant_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Realistic logistics tables
    cursor.execute('''
        CREATE TABLE shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            reading REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Obfuscated table for the flag
    cursor.execute('''
        CREATE TABLE vbl_inventory_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metadata_key TEXT NOT NULL,
            config_value TEXT NOT NULL
        )
    ''')

    # Seed Data
    cursor.execute("INSERT INTO shipments (tracking_number, origin, destination, status) VALUES ('VBL-7721-X', 'Berlin, DE', 'Singapore, SG', 'In Transit')")
    cursor.execute("INSERT INTO shipments (tracking_number, origin, destination, status) VALUES ('VBL-1029-A', 'Rotterdam, NL', 'New York, US', 'Processing')")
    cursor.execute("INSERT INTO shipments (tracking_number, origin, destination, status) VALUES ('VBL-9920-C', 'São Paulo, BR', 'London, UK', 'Delivered')")

    cursor.execute("INSERT INTO telemetry (sensor_id, reading, timestamp) VALUES ('TEMP-01', 4.2, '2023-10-27 10:00:00')")
    cursor.execute("INSERT INTO telemetry (sensor_id, reading, timestamp) VALUES ('TEMP-02', 3.8, '2023-10-27 10:05:00')")
    cursor.execute("INSERT INTO telemetry (sensor_id, reading, timestamp) VALUES ('HUM-01', 45.1, '2023-10-27 10:10:00')")

    cursor.execute("INSERT INTO vbl_inventory_metadata (metadata_key, config_value) VALUES ('system_build_version', 'v4.2.1-stable')")
    
    # Read flag from /flag.txt
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    cursor.execute("INSERT INTO vbl_inventory_metadata (metadata_key, config_value) VALUES ('root_access_node_id', ?)", (flag,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()