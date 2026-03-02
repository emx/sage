import sqlite3
import os

def init():
    db_path = '/tmp/velovortex.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, shipment_id TEXT, destination TEXT, cargo_type TEXT, status TEXT, driver_id INTEGER)''')
    c.execute('''CREATE TABLE drivers (id INTEGER PRIMARY KEY, name TEXT, license_no TEXT, vin TEXT, rating REAL)''')
    c.execute('''CREATE TABLE internal_audit (id INTEGER PRIMARY KEY, setting_key TEXT, setting_value TEXT)''')
    
    # Realistic Seed Data
    drivers = [
        (1, 'Marcus Thorne', 'DL-992831', '1V9HG5829BK', 4.8),
        (2, 'Elena Rodriguez', 'DL-110293', '3C6UR1290AL', 4.9),
        (3, 'Sarah Jenkins', 'DL-448291', '5F2KM9938PQ', 4.7)
    ]
    c.executemany('INSERT INTO drivers VALUES (?,?,?,?,?)', drivers)
    
    shipments = [
        (1, 'VV-8821', 'Berlin, DE', 'Industrial Turbines', 'In-Transit', 1),
        (2, 'VV-9902', 'Lyon, FR', 'Medical Supplies', 'Pending', 2),
        (3, 'VV-1123', 'Madrid, ES', 'Electronics', 'Delivered', 3),
        (4, 'VV-4456', 'Warsaw, PL', 'Textiles', 'In-Transit', 1),
        (5, 'VV-5567', 'Rome, IT', 'Perishables', 'Delayed', 2)
    ]
    c.executemany('INSERT INTO shipments VALUES (?,?,?,?,?,?)', shipments)
    
    # The Flag Isolation
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{MOCK_FLAG_FOR_LOCAL_TESTING}"
        
    c.execute('INSERT INTO internal_audit (setting_key, setting_value) VALUES (?, ?)', ('system_integrity_hash', flag))
    c.execute('INSERT INTO internal_audit (setting_key, setting_value) VALUES (?, ?)', ('api_v3_endpoint', 'https://api-internal.velovortex.logistics/v3'))
    
    conn.commit()
    conn.close()
    print("Database initialized at /tmp/velovortex.db")

if __name__ == '__main__':
    init()