import sqlite3
import os

def init():
    db_path = '/tmp/logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE silos (
            id INTEGER PRIMARY KEY,
            name TEXT,
            grain_type TEXT,
            fill_level INTEGER,
            capacity INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE shipments (
            id INTEGER PRIMARY KEY,
            shipment_id TEXT,
            grain_type TEXT,
            quantity INTEGER,
            status TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE inspections (
            id INTEGER PRIMARY KEY,
            inspector_id TEXT,
            inspection_date TEXT,
            result TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE inventory_meta (
            id INTEGER PRIMARY KEY,
            meta_key TEXT,
            meta_value TEXT
        )
    ''')
    
    # Seed Data
    cursor.execute("INSERT INTO silos VALUES (1, 'Alpha-01', 'Hard Red Wheat', 65, 5000)")
    cursor.execute("INSERT INTO silos VALUES (2, 'Beta-05', 'Barley', 82, 3500)")
    cursor.execute("INSERT INTO silos VALUES (3, 'Gamma-09', 'Yellow Corn', 12, 8000)")
    
    cursor.execute("INSERT INTO shipments (shipment_id, grain_type, quantity, status) VALUES ('VP-8821', 'Wheat', 450, 'Departed')")
    cursor.execute("INSERT INTO shipments (shipment_id, grain_type, quantity, status) VALUES ('VP-9902', 'Corn', 1200, 'In Transit')")
    cursor.execute("INSERT INTO shipments (shipment_id, grain_type, quantity, status) VALUES ('VP-4410', 'Barley', 300, 'Arrived')")
    
    cursor.execute("INSERT INTO inspections (inspector_id, inspection_date, result) VALUES ('INS-44', '2024-02-12', 'Pass')")
    cursor.execute("INSERT INTO inspections (inspector_id, inspection_date, result) VALUES ('INS-44', '2024-02-15', 'Pass')")
    cursor.execute("INSERT INTO inspections (inspector_id, inspection_date, result) VALUES ('INS-12', '2024-03-01', 'Review Required')")
    
    # Obfuscated table for flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO inventory_meta (meta_key, meta_value) VALUES ('system_integrity_token', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO inventory_meta (meta_key, meta_value) VALUES ('system_integrity_token', 'FLAG_NOT_FOUND')")
    
    cursor.execute("INSERT INTO inventory_meta (meta_key, meta_value) VALUES ('sensor_api_version', '2.4.1')")
    cursor.execute("INSERT INTO inventory_meta (meta_key, meta_value) VALUES ('maintenance_schedule', '2024-Q4')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()