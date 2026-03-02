import sqlite3
import os

def init():
    db_path = '/tmp/logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, sku TEXT, name TEXT, quantity INTEGER, location TEXT, temp REAL)')
    cursor.execute('CREATE TABLE fleet (id INTEGER PRIMARY KEY, name TEXT, route TEXT, status TEXT)')
    cursor.execute('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, action TEXT, details TEXT)')
    # Obfuscated table for flag
    cursor.execute('CREATE TABLE system_metadata (id INTEGER PRIMARY KEY, tag TEXT, backup_data TEXT)')
    
    # Seed Data
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'VV_Admin_2024_!@#', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'logistics_2024', 'viewer')")
    
    inventory_data = [
        ('VV-APL-001', 'Honeycrisp Apples', 1200, 'Salinas Hub', 2.2),
        ('VV-AVO-002', 'Hass Avocados', 850, 'Central Valley', 4.5),
        ('VV-SPI-003', 'Baby Spinach', 3000, 'Everglades DC', 1.1),
        ('VV-TOM-004', 'Heirloom Tomatoes', 500, 'Salinas Hub', 10.0)
    ]
    cursor.executemany('INSERT INTO inventory (sku, name, quantity, location, temp) VALUES (?,?,?,?,?)', inventory_data)
    
    fleet_data = [
        ('John Miller', 'CA-SR-101', 'In Transit'),
        ('Sarah Chen', 'FL-MIA-02', 'Loading'),
        ('Marcus Wright', 'TX-DAL-09', 'Resting')
    ]
    cursor.executemany('INSERT INTO fleet (name, route, status) VALUES (?,?,?)', fleet_data)
    
    audit_data = [
        ('LOGIN', 'User admin logged in from 192.168.1.5'),
        ('TEMP_ALERT', 'Warehouse Salinas Hub sensor reported 3.5C'),
        ('DISPATCH', 'Driver John Miller departed Salinas Hub'),
        ('LOGIN', 'User guest logged in from mobile app')
    ]
    cursor.executemany('INSERT INTO audit_logs (action, details) VALUES (?,?)', audit_data)
    
    # Flag Isolation: Read from /flag.txt and put in DB
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_metadata (tag, backup_data) VALUES ('flag', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO system_metadata (tag, backup_data) VALUES ('flag', 'ERROR_READING_FLAG')")

    cursor.execute("INSERT INTO system_metadata (tag, backup_data) VALUES ('version', '2.4.1')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()