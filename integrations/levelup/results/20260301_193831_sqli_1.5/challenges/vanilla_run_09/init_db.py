import sqlite3
import os

def init():
    db_path = '/tmp/thalassa.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create tables
    c.execute('CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, registration TEXT, status TEXT)')
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, vessel_id INTEGER, container_id TEXT, destination TEXT, cargo_type TEXT)')
    c.execute('CREATE TABLE internal_routing_metadata (id INTEGER PRIMARY KEY, secret_key TEXT, routing_secret TEXT)')

    # Seed Vessels
    vessels = [
        (1, 'Poseidon Explorer', 'IMO 9315422', 'In Transit'),
        (2, 'Thalassa Blue', 'IMO 9283741', 'Docked'),
        (3, 'Aegean Merchant', 'IMO 9403322', 'Maintenance'),
        (4, 'Oceanic Titan', 'IMO 9552190', 'In Transit')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?)', vessels)

    # Seed Manifests
    manifests = [
        (1, 1, 'CONT-A12', 'Rotterdam', 'Electronics'),
        (2, 1, 'CONT-B44', 'Rotterdam', 'Auto Parts'),
        (3, 2, 'CONT-Z99', 'Piraeus', 'Textiles'),
        (4, 4, 'CONT-H01', 'Singapore', 'Medical Supplies')
    ]
    c.executemany('INSERT INTO manifests VALUES (?,?,?,?,?)', manifests)

    # Seed Flag into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute('INSERT INTO internal_routing_metadata (secret_key, routing_secret) VALUES (?, ?)', ('system_flag', flag))
    except Exception as e:
        print(f"Error reading flag: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()