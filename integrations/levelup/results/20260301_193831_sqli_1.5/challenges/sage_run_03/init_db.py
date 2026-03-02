import sqlite3
import os

def init():
    db = sqlite3.connect('/tmp/verdant.db')
    cursor = db.cursor()
    
    # Realistic data tables
    cursor.execute('''CREATE TABLE silo_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        silo_serial TEXT UNIQUE,
        location TEXT,
        capacity INTEGER,
        fill_level INTEGER,
        commodity TEXT
    )''')
    
    cursor.execute('''CREATE TABLE shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin TEXT,
        destination TEXT,
        driver_name TEXT,
        status TEXT
    )''')
    
    # Obfuscated table for secrets
    cursor.execute('''CREATE TABLE app_config (
        config_id INTEGER PRIMARY KEY,
        config_key TEXT,
        config_value TEXT
    )''')
    
    # Insert seed data
    silos = [
        ('S-101', 'Omaha Hub - Section A', 5000, 82, 'Winter Wheat'),
        ('S-102', 'Omaha Hub - Section B', 5000, 45, 'Yellow Corn'),
        ('S-205', 'Des Moines Regional', 12000, 12, 'Organic Soy'),
        ('S-440', 'Kansas City Distribution', 8000, 94, 'Fertilizer 10-10-10')
    ]
    cursor.executemany('INSERT INTO silo_metadata (silo_serial, location, capacity, fill_level, commodity) VALUES (?,?,?,?,?)', silos)
    
    shipments = [
        ('Omaha', 'Chicago', 'Miller, J.', 'In Transit'),
        ('Des Moines', 'St. Louis', 'Vance, R.', 'Loading'),
        ('Kansas City', 'Denver', 'Hardy, L.', 'Arrived')
    ]
    cursor.executemany('INSERT INTO shipments (origin, destination, driver_name, status) VALUES (?,?,?,?)', shipments)
    
    # Read flag and hide it
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    cursor.execute("INSERT INTO app_config (config_key, config_value) VALUES ('api_version', '2.4.1')")
    cursor.execute("INSERT INTO app_config (config_key, config_value) VALUES ('emergency_override_code', ?)", (flag,))
    
    db.commit()
    db.close()

if __name__ == '__main__':
    init()