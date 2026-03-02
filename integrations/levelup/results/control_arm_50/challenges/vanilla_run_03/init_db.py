import sqlite3
import os

def init():
    db_path = '/tmp/velolink.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('CREATE TABLE dispatchers (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('INSERT INTO dispatchers (username, password) VALUES ("d.watkins", "password123"), ("a.chen", "veloSecure2024!")')

    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, origin TEXT, destination TEXT, cargo_type TEXT, status TEXT)')
    c.execute('INSERT INTO manifests (origin, destination, cargo_type, status) VALUES ("Rotterdam", "New York", "Electronics", "In Transit"), ("Shanghai", "Los Angeles", "Textiles", "Pending"), ("Hamburg", "Dubai", "Machinery", "Loading")')

    c.execute('CREATE TABLE drivers (id INTEGER PRIMARY KEY, full_name TEXT, license_id TEXT, region TEXT, expiry_date TEXT)')
    c.execute('INSERT INTO drivers (full_name, license_id, region, expiry_date) VALUES ("James Miller", "TX-99201", "North America", "2026-12-01"), ("Elena Rodriguez", "EU-88210", "Europe", "2025-05-14")')

    c.execute('CREATE TABLE shipping_nodes (id INTEGER PRIMARY KEY, node_name TEXT, status TEXT, load_factor FLOAT)')
    c.execute('INSERT INTO shipping_nodes (node_name, status, load_factor) VALUES ("Atlantic-Hub-01", "Operational", 0.75), ("Pacific-Terminal-B", "Standby", 0.12), ("Euro-Gateway-Alpha", "Operational", 0.88)')

    # Obfuscated table for flag
    c.execute('CREATE TABLE internal_system_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)')
    
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute('INSERT INTO internal_system_settings (setting_name, setting_value) VALUES ("root_access_canary", ?)', (flag,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()