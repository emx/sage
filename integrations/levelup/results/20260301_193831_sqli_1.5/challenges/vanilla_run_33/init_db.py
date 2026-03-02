import sqlite3
import os

def init():
    db_path = '/tmp/verdant_logistics.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('''CREATE TABLE grain_inventory (id INTEGER PRIMARY KEY, silo_name TEXT, grain_type TEXT, capacity REAL)''')
    c.execute('''CREATE TABLE shipping_manifests (id INTEGER PRIMARY KEY, manifest_id TEXT, destination TEXT, quantity REAL, shipping_date TEXT)''')
    c.execute('''CREATE TABLE silo_health_metrics (id INTEGER PRIMARY KEY, silo_id INTEGER, temperature REAL, recorded_at TEXT)''')
    c.execute('''CREATE TABLE internal_system_registry (id INTEGER PRIMARY KEY, registry_key TEXT, registry_value TEXT)''')

    # Seed Data
    c.execute("INSERT INTO grain_inventory (silo_name, grain_type, capacity) VALUES ('Silo-Alpha', 'Hard Red Winter Wheat', 85.5)")
    c.execute("INSERT INTO grain_inventory (silo_name, grain_type, capacity) VALUES ('Silo-Bravo', 'Soft White Wheat', 92.1)")
    c.execute("INSERT INTO grain_inventory (silo_name, grain_type, capacity) VALUES ('Silo-Charlie', 'Yellow Corn', 45.0)")

    c.execute("INSERT INTO shipping_manifests (manifest_id, destination, quantity, shipping_date) VALUES ('VC-9921', 'Rotterdam Port', 12000.5, '2023-10-12')")
    c.execute("INSERT INTO shipping_manifests (manifest_id, destination, quantity, shipping_date) VALUES ('VC-9922', 'Port of Singapore', 8500.0, '2023-10-14')")

    # Metrics for Silo 1
    import datetime
    for i in range(24):
        time_str = (datetime.datetime.now() - datetime.timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO silo_health_metrics (silo_id, temperature, recorded_at) VALUES (?, ?, ?)", (1, 18.5 + (i * 0.1), time_str))

    # Insert the Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{local_test_flag}"
        
    c.execute("INSERT INTO internal_system_registry (registry_key, registry_value) VALUES ('system_flag', ?)", (flag,))
    c.execute("INSERT INTO internal_system_registry (registry_key, registry_value) VALUES ('admin_email', 'ops-manager@verdantchain.io')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()