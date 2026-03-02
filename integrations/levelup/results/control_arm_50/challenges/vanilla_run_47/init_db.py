import sqlite3
import os

def init():
    db_path = '/tmp/verdant_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE shipments (tracking_id TEXT, destination TEXT, status TEXT, client_id TEXT)''')
    c.execute('''CREATE TABLE inventory (id INTEGER PRIMARY KEY, item_name TEXT, category TEXT, quantity INTEGER, warehouse TEXT)''')
    c.execute('''CREATE TABLE assets (id INTEGER PRIMARY KEY, name TEXT, asset_tag TEXT, location TEXT, last_inspected TEXT)''')
    c.execute('''CREATE TABLE internal_vault (id INTEGER PRIMARY KEY, config_key TEXT, data TEXT)''')

    c.execute("INSERT INTO shipments VALUES ('VA-9901', 'Berlin, DE', 'In Transit', 'C-4412')")
    c.execute("INSERT INTO inventory (item_name, category, quantity, warehouse) VALUES ('Titanium Rods', 'Metals', 450, 'WH-ALPHA')")
    c.execute("INSERT INTO assets (name, asset_tag, location, last_inspected) VALUES ('Heavy Forklift', 'AX-001', 'Sector 7', '2024-01-10')")
    
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    c.execute("INSERT INTO internal_vault (config_key, data) VALUES ('system_integrity_hash', ?)", (flag,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()