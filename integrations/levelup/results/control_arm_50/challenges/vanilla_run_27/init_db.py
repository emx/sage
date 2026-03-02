import sqlite3
import os

def init():
    db = sqlite3.connect('vantage.db')
    cursor = db.cursor()

    # Tables
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, tracking_no TEXT, destination TEXT, weight INTEGER, status TEXT)')
    cursor.execute('CREATE TABLE carriers (id INTEGER PRIMARY KEY, carrier_id TEXT, name TEXT, region TEXT, status TEXT)')
    cursor.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, sku TEXT, name TEXT, quantity INTEGER, location TEXT)')
    cursor.execute('CREATE TABLE site_analytics_tracking (id INTEGER PRIMARY KEY, session_blob TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'Th3_M4st3r_Of_L0g1st1cs_2024!', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'viewer')")
    
    manifests_data = [
        ('VF-90210', 'Singapore', 1200, 'Processing'),
        ('VF-44122', 'Rotterdam', 5400, 'In-Transit'),
        ('VF-11092', 'Dubai', 3100, 'Arrived'),
        ('VF-88213', 'New Jersey', 900, 'Departed'),
        ('VF-77120', 'Tokyo', 2200, 'Delayed')
    ]
    cursor.executemany('INSERT INTO manifests (tracking_no, destination, weight, status) VALUES (?, ?, ?, ?)', manifests_data)

    cursor.execute("INSERT INTO inventory (sku, name, quantity, location) VALUES ('VF-ITM-001', 'High-Density Pallets', 500, 'Zone-A')")
    cursor.execute("INSERT INTO inventory (sku, name, quantity, location) VALUES ('VF-ITM-099', 'Forklift Batteries', 12, 'Zone-C')")

    # Insert Flag into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute('INSERT INTO site_analytics_tracking (session_blob) VALUES (?)', (flag,))
    except:
        cursor.execute('INSERT INTO site_analytics_tracking (session_blob) VALUES (?)', ('LEVELUP{PLACEHOLDER_FLAG}',))

    db.commit()
    db.close()

if __name__ == '__main__':
    init()