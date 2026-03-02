import sqlite3
import os

def init():
    db_path = '/tmp/aether_logistics.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Users table
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute('INSERT INTO users (username, password, role) VALUES ("admin", "super_secret_Aether_2024_root", "admin")')
    cursor.execute('INSERT INTO users (username, password, role) VALUES ("analyst", "AetherAnalyst2024!", "analyst")')

    # Shipments table
    cursor.execute('CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_number TEXT, origin TEXT, destination TEXT, status TEXT)')
    shipments = [
        ('ALT-9001-X', 'Berlin, DE', 'Singapore, SG', 'In Transit'),
        ('ALT-2044-B', 'Chicago, US', 'London, UK', 'Delivered'),
        ('ALT-1182-C', 'Tokyo, JP', 'Sydney, AU', 'In Transit'),
        ('ALT-5561-Z', 'Paris, FR', 'New York, US', 'Processing'),
        ('ALT-8820-K', 'Toronto, CA', 'Dubai, AE', 'In Transit')
    ]
    cursor.executemany('INSERT INTO shipments (tracking_number, origin, destination, status) VALUES (?, ?, ?, ?)', shipments)

    # Obfuscated vault table for the flag
    cursor.execute('CREATE TABLE app_metadata_internal (id INTEGER PRIMARY KEY, config_id INTEGER, meta_key TEXT, meta_value TEXT)')
    
    flag = open('/flag.txt', 'r').read().strip()
    cursor.execute('INSERT INTO app_metadata_internal (config_id, meta_key, meta_value) VALUES (1337, "master_internal_signature", ?)', (flag,))
    
    db.commit()
    db.close()
    print("Database initialized at /tmp/aether_logistics.db")

if __name__ == '__main__':
    init()