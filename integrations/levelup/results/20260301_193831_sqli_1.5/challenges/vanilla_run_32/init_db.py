import sqlite3
import os

def init():
    db_path = "/tmp/maritime.db"
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, registry TEXT, type TEXT)''')
    c.execute('''CREATE TABLE manifests (id INTEGER PRIMARY KEY, vessel_id INTEGER, cargo_name TEXT, destination TEXT, cargo_weight INTEGER, clearance_date TEXT)''')
    c.execute('''CREATE TABLE system_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)''')

    # Seed Vessels
    vessels = [
        (101, 'Abyssal Voyager', 'Panama', 'Container Ship'),
        (102, 'Northern Star', 'Norway', 'Tanker'),
        (103, 'Global Horizon', 'Liberia', 'Bulk Carrier'),
        (104, 'Oceanic Crest', 'Marshall Islands', 'Reefer'),
        (105, 'Deep Sea Pioneer', 'Singapore', 'Tug')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?)', vessels)

    # Seed Manifests
    manifests = [
        (1, 101, 'Industrial Machinery', 'Rotterdam', 450, '2023-10-15'),
        (2, 101, 'Consumer Electronics', 'Rotterdam', 120, '2023-10-15'),
        (3, 102, 'Crude Oil', 'Houston', 50000, '2023-11-02'),
        (4, 103, 'Grain Silos', 'Shanghai', 2200, '2023-11-05'),
        (5, 104, 'Perishable Foods', 'London', 85, '2023-11-10'),
        (6, 105, 'Harbor Equipment', 'Singapore', 30, '2023-11-12')
    ]
    c.executemany('INSERT INTO manifests VALUES (?,?,?,?,?,?)', manifests)

    # Seed System Settings (Flag Isolation)
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('maintenance_key', ?)", (flag,))
    c.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('api_version', 'v1.4.2-stable')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()