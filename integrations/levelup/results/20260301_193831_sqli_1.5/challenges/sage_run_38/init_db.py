import sqlite3
import os

def init():
    db_path = '/tmp/velolink.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create standard tables
    c.execute('''CREATE TABLE vessels 
                 (id INTEGER PRIMARY KEY, name TEXT, flag_state TEXT, vessel_type TEXT, status TEXT)''')
    
    c.execute('''CREATE TABLE manifests 
                 (id INTEGER PRIMARY KEY, bol_number TEXT, vessel_id INTEGER, destination TEXT, weight REAL)''')

    # Insert realistic seed data
    vessels = [
        (1, 'MV Oceanic Star', 'Panama', 'Container Ship', 'In Transit'),
        (2, 'Ever Given', 'Panama', 'Ultra Large Container Vessel', 'Anchored'),
        (3, 'Baltic Mercury', 'Malta', 'Ro-Ro Cargo', 'Docked'),
        (4, 'Pacific Wanderer', 'Marshall Islands', 'Bulk Carrier', 'In Transit'),
        (5, 'Nordic Frost', 'Norway', 'LPG Tanker', 'Under Maintenance'),
        (6, 'Atlantic Spirit', 'Bahamas', 'Product Tanker', 'In Transit')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?,?)', vessels)

    # Create obfuscated secrets table
    c.execute('''CREATE TABLE internal_node_cfg 
                 (id INTEGER PRIMARY KEY, node_name TEXT, node_secret TEXT)''')
    
    # Read flag from isolated file
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag_for_dev}"

    c.execute("INSERT INTO internal_node_cfg (node_name, node_secret) VALUES ('primary_vessel_telemetry_hub', ?)", (flag,))

    conn.commit()
    conn.close()
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()