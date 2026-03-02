import sqlite3
import os

def init():
    conn = sqlite3.connect('/app/verdant.db')
    cursor = conn.cursor()

    # Business Tables
    cursor.execute('CREATE TABLE harvest_records (id INTEGER PRIMARY KEY, crop_name TEXT, yield INTEGER, zone TEXT, harvest_date TEXT)')
    cursor.execute('CREATE TABLE soil_metrics (id INTEGER PRIMARY KEY, zone TEXT, ph_level REAL, nitrogen INTEGER, phosphorus INTEGER, potassium INTEGER)')
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    
    # Hidden System Table
    cursor.execute('CREATE TABLE verdant_internal_registry (id INTEGER PRIMARY KEY, registry_key TEXT, registry_data TEXT)')

    # Seed Data
    harvests = [
        ('Winter Wheat', 450, 'Zone A', '2023-11-15'),
        ('Sweet Corn', 820, 'Zone B', '2023-10-02'),
        ('Soybeans', 310, 'Zone C', '2023-09-20'),
        ('Organic Barley', 215, 'Zone A', '2023-12-01'),
        ('Russet Potatoes', 1100, 'Zone D', '2023-11-20')
    ]
    cursor.executemany('INSERT INTO harvest_records (crop_name, yield, zone, harvest_date) VALUES (?, ?, ?, ?)', harvests)

    soil = [
        ('Zone A', 6.5, 42, 18, 205),
        ('Zone B', 7.1, 55, 22, 190),
        ('Zone C', 5.8, 38, 15, 230),
        ('Zone D', 6.8, 60, 25, 215)
    ]
    cursor.executemany('INSERT INTO soil_metrics (zone, ph_level, nitrogen, phosphorus, potassium) VALUES (?, ?, ?, ?, ?)', soil)

    # Insert the Flag into the registry
    with open('/flag.txt', 'r') as f:
        flag_content = f.read().strip()
    
    cursor.execute('INSERT INTO verdant_internal_registry (registry_key, registry_data) VALUES ("emergency_override_key", ?)', (flag_content,))
    cursor.execute('INSERT INTO verdant_internal_registry (registry_key, registry_data) VALUES ("api_secret_v2", "d8a2c1e6f9b2c3d4a5b6c7d8e9f0a1b2")')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()