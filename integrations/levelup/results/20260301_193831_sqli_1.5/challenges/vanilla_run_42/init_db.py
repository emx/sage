import sqlite3
import os

def init():
    db_path = '/tmp/vanguardia.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Users Table
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute("INSERT INTO users VALUES (1, 'admin', 'K3y_T0_Th3_St4rs_2024!', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'guest', 'guest123', 'viewer')")

    # Manifests Table
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, cargo_id TEXT, destination TEXT, weight INTEGER, status TEXT, timestamp DATETIME)')
    manifest_data = [
        ('C-1042', 'Lunar Gateway', 450, 'Delivered', '2023-10-12 14:20:00'),
        ('C-2091', 'Mars-Orbit-Alpha', 1200, 'In Transit', '2023-11-05 09:15:00'),
        ('C-0082', 'ISS Repair Hub', 85, 'Completed', '2023-09-20 18:45:00'),
        ('C-5512', 'Vanguard-1 Station', 220, 'Scheduled', '2024-01-10 11:00:00')
    ]
    c.executemany("INSERT INTO manifests (cargo_id, destination, weight, status, timestamp) VALUES (?, ?, ?, ?, ?)", manifest_data)

    # Obfuscated Registry Table (Target)
    c.execute('CREATE TABLE core_registry (id INTEGER PRIMARY KEY, registry_key TEXT, registry_data TEXT)')
    
    flag = "UNSET"
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder}"

    c.execute("INSERT INTO core_registry (registry_key, registry_data) VALUES ('orbital_vanguard_key', ?)", (flag,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()