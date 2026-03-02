import sqlite3
import os

DB_PATH = '/tmp/thalassa.db'

def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Shipments Table
    c.execute('''CREATE TABLE shipments 
                 (id INTEGER PRIMARY KEY, container_id TEXT, vessel TEXT, destination TEXT, status TEXT)''')
    
    # Seed data carefully crafted for ORDER BY boolean extraction
    # ID sort: Zephyr (1), Albatross (2), Gaea (3)
    # Vessel sort: Albatross (2), Gaea (3), Zephyr (1)
    c.execute("INSERT INTO shipments VALUES (1, 'CONT-102', 'Zephyr', 'Singapore', 'In Transit')")
    c.execute("INSERT INTO shipments VALUES (2, 'CONT-505', 'Albatross', 'Rotterdam', 'Docked')")
    c.execute("INSERT INTO shipments VALUES (3, 'CONT-909', 'Gaea', 'Hamburg', 'Loading')")

    # Vessels Table
    c.execute('''CREATE TABLE vessels 
                 (id INTEGER PRIMARY KEY, name TEXT, registry TEXT, capacity INTEGER)''')
    c.execute("INSERT INTO vessels VALUES (1, 'Albatross', 'Panama', 18000)")
    c.execute("INSERT INTO vessels VALUES (2, 'Zephyr', 'Liberia', 15000)")
    c.execute("INSERT INTO vessels VALUES (3, 'Gaea', 'Marshall Islands', 22000)")

    # Obfuscated Flag Table
    c.execute('''CREATE TABLE site_telemetry 
                 (id INTEGER PRIMARY KEY, event_type TEXT, event_data TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert the flag from the file
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO site_telemetry (event_type, event_data) VALUES ('system_heartbeat', '0x99281a')")
    c.execute("INSERT INTO site_telemetry (event_type, event_data) VALUES ('backup_vault_checksum', ?)", (flag,))
    c.execute("INSERT INTO site_telemetry (event_type, event_data) VALUES ('node_sync_status', 'synchronized')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()