import sqlite3
import os

def init():
    conn = sqlite3.connect('voyant.db')
    c = conn.cursor()

    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, waybill TEXT, origin TEXT, destination TEXT, status TEXT)')
    manifests = [
        ('WB-99201', 'Singapore', 'Rotterdam', 'In Transit'),
        ('WB-11029', 'Shanghai', 'Los Angeles', 'Processing'),
        ('WB-44920', 'Hamburg', 'New York', 'Delivered'),
        ('WB-33012', 'Dubai', 'Mumbai', 'In Transit')
    ]
    c.executemany('INSERT INTO manifests (waybill, origin, destination, status) VALUES (?,?,?,?)', manifests)

    c.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER, warehouse_id INTEGER)')
    items = [
        ('Steel Cargo Container 40ft', 150, 1),
        ('Pallet Jack Hydraulic', 45, 1),
        ('Heavy Duty Winch', 12, 1),
        ('Industrial Forklift', 8, 1),
        ('Shipping Grade Strapping (Roll)', 500, 1)
    ]
    c.executemany('INSERT INTO inventory (item_name, quantity, warehouse_id) VALUES (?,?,?)', items)

    # The Obfuscated Table for the flag
    c.execute('CREATE TABLE internal_metadata (id INTEGER PRIMARY KEY, conf_key TEXT, conf_val TEXT)')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag_for_testing}'

    c.execute("INSERT INTO internal_metadata (conf_key, conf_val) VALUES ('system_version', 'v4.2.1-stable')")
    c.execute("INSERT INTO internal_metadata (conf_key, conf_val) VALUES ('master_config_secret', ?)", (flag,))
    c.execute("INSERT INTO internal_metadata (conf_key, conf_val) VALUES ('region_code', 'GLOBAL-HQ')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()