import sqlite3
import os

def init():
    conn = sqlite3.connect('/tmp/aetherlogix.db')
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'K33p_It_S4f3_2024!', 'Administrator')")
    cursor.execute("INSERT INTO users VALUES (2, 'guest', 'guest', 'Coordinator')")
    
    # Manifests Table
    cursor.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, manifest_id TEXT, vessel_name TEXT, destination TEXT, status TEXT)')
    shipments = [
        ('MNF-8821', 'SS Borealis', 'Singapore', 'Arrived'),
        ('MNF-3902', 'Oceanic Horizon', 'Rotterdam', 'In-Transit'),
        ('MNF-1109', 'Titan Carrier', 'Los Angeles', 'Processing'),
        ('MNF-7723', 'Sea Voyager', 'Dubai', 'Departed'),
        ('MNF-5541', 'Global Express', 'Hamburg', 'Arrived')
    ]
    for s in shipments:
        cursor.execute("INSERT INTO manifests (manifest_id, vessel_name, destination, status) VALUES (?, ?, ?, ?)", s)

    # Vessel Registry
    cursor.execute('CREATE TABLE vessel_registry (id INTEGER PRIMARY KEY, name TEXT, registry_num TEXT, status TEXT)')
    cursor.execute("INSERT INTO vessel_registry VALUES (1, 'SS Borealis', 'REG-10293', 'Active')")
    cursor.execute("INSERT INTO vessel_registry VALUES (2, 'Oceanic Horizon', 'REG-55213', 'Active')")

    # Obfuscated Flag Table
    cursor.execute('CREATE TABLE billing_config (id INTEGER PRIMARY KEY, config_id TEXT, config_value TEXT)')
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    cursor.execute("INSERT INTO billing_config (config_id, config_value) VALUES ('global_flag', ?)", (flag,))
    cursor.execute("INSERT INTO billing_config (config_id, config_value) VALUES ('api_endpoint', 'https://internal-api.aetherlogix.net/v2')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()