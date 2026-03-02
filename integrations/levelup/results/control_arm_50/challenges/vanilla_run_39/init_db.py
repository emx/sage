import sqlite3
import os

def init():
    db_path = '/tmp/verdant_axis.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table 1: Inventory
    cursor.execute('''
    CREATE TABLE silo_inventory (
        silo_id INTEGER PRIMARY KEY,
        location TEXT NOT NULL,
        grain_type TEXT NOT NULL,
        moisture_level REAL,
        capacity_pct INTEGER,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Table 2: Chemical Logs
    cursor.execute('''
    CREATE TABLE chemical_applications (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        batch_id TEXT,
        chemical_name TEXT,
        dosage_ml INTEGER
    )''')

    # Table 3: Obfuscated Flag Table
    cursor.execute('''
    CREATE TABLE node_configuration_v2 (
        config_id INTEGER PRIMARY KEY,
        setting_name TEXT,
        setting_value TEXT
    )''')

    # Seed Data
    cursor.execute("INSERT INTO silo_inventory (location, grain_type, moisture_level, capacity_pct) VALUES ('Nebraska Hub-4', 'Hard Red Winter Wheat', 12.4, 85)")
    cursor.execute("INSERT INTO silo_inventory (location, grain_type, moisture_level, capacity_pct) VALUES ('Iowa Site-A12', 'Yellow Dent Corn', 14.1, 92)")
    cursor.execute("INSERT INTO silo_inventory (location, grain_type, moisture_level, capacity_pct) VALUES ('Bavaria Collective', 'Two-Row Malt Barley', 11.8, 60)")
    cursor.execute("INSERT INTO silo_inventory (location, grain_type, moisture_level, capacity_pct) VALUES ('Saskatchewan East', 'Canola Prime', 8.5, 45)")

    cursor.execute("INSERT INTO chemical_applications (batch_id, chemical_name, dosage_ml) VALUES ('BATCH-9921', 'Glyphos-Max', 500)")
    cursor.execute("INSERT INTO chemical_applications (batch_id, chemical_name, dosage_ml) VALUES ('BATCH-8812', 'Fungicide-Alpha', 250)")

    # Insert Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO node_configuration_v2 (setting_name, setting_value) VALUES ('system_access_token', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO node_configuration_v2 (setting_name, setting_value) VALUES ('system_access_token', 'FLAG_NOT_FOUND')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()