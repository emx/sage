import sqlite3
import os

def init():
    db_path = '/tmp/verdant.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Public tables
    c.execute('CREATE TABLE parcels (id INTEGER PRIMARY KEY, name TEXT, location TEXT, owner_id TEXT)')
    c.execute('CREATE TABLE soil_samples (id INTEGER PRIMARY KEY, parcel_id INTEGER, nitrogen FLOAT, phosphorus FLOAT, ph_level FLOAT, recorded_at TIMESTAMP)')
    
    # Obfuscated system table
    c.execute('CREATE TABLE system_registry (reg_id INTEGER PRIMARY KEY, reg_key TEXT, reg_value TEXT)')

    # Seed public data
    parcels = [
        (1, 'North Valley Plot A', '45.523,-122.676', 'US-7782'),
        (2, 'East Ridge Terrace', '45.512,-122.621', 'US-1102'),
        (3, 'Highland Marshlands', '45.589,-122.599', 'US-4491')
    ]
    c.executemany('INSERT INTO parcels VALUES (?,?,?,?)', parcels)

    samples = [
        (1, 1, 45.2, 12.5, 6.8, '2023-10-01 08:00:00'),
        (2, 1, 44.8, 13.1, 6.7, '2023-10-02 08:30:00'),
        (3, 1, 46.1, 12.0, 6.9, '2023-10-03 07:45:00'),
        (4, 2, 38.5, 15.2, 7.2, '2023-10-01 09:00:00'),
        (5, 3, 55.0, 10.2, 6.2, '2023-10-01 10:15:00')
    ]
    c.executemany('INSERT INTO soil_samples VALUES (?,?,?,?,?,?)', samples)

    # Insert flag from root-owned file
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute('INSERT INTO system_registry (reg_key, reg_value) VALUES (?, ?)', ('internal_system_flag', flag))
    c.execute('INSERT INTO system_registry (reg_key, reg_value) VALUES (?, ?)', ('api_version', '4.2.1-stable'))
    c.execute('INSERT INTO system_registry (reg_key, reg_value) VALUES (?, ?)', ('maintenance_mode', 'off'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()