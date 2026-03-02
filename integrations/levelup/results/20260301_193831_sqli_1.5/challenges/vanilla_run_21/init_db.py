import sqlite3
import os

def init():
    db_path = '/app/verdant_pulse.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Application Data
    cursor.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, name TEXT, category TEXT, stock INTEGER)')
    cursor.execute("INSERT INTO inventory (name, category, stock) VALUES ('Phosphorus Max', 'Chemicals', 450)")
    cursor.execute("INSERT INTO inventory (name, category, stock) VALUES ('Nitrogen Plus', 'Chemicals', 120)")
    cursor.execute("INSERT INTO inventory (name, category, stock) VALUES ('Hybrid Corn Seeds', 'Seeds', 1000)")
    cursor.execute("INSERT INTO inventory (name, category, stock) VALUES ('Organic Soy Seeds', 'Seeds', 850)")
    cursor.execute("INSERT INTO inventory (name, category, stock) VALUES ('Potash Premix', 'Chemicals', 300)")

    # Telemetry Nodes
    cursor.execute('CREATE TABLE sensor_nodes (id INTEGER PRIMARY KEY, location TEXT, status TEXT)')
    cursor.execute("INSERT INTO sensor_nodes (location, status) VALUES ('Sector-7G', 'Active')")
    cursor.execute("INSERT INTO sensor_nodes (location, status) VALUES ('Sector-12B', 'Maintenance')")

    # Obfuscated Flag Table
    cursor.execute('CREATE TABLE app_metadata (id INTEGER PRIMARY KEY, key TEXT, val TEXT)')
    cursor.execute("INSERT INTO app_metadata (key, val) VALUES ('system_build_version', 'v2.4.1-gold')")
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO app_metadata (key, val) VALUES ('emergency_node_recovery_key', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO app_metadata (key, val) VALUES ('emergency_node_recovery_key', 'FLAG_NOT_FOUND')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()