import sqlite3
import os

def init():
    # Use /tmp for the database as required for read-only FS
    db_path = '/tmp/veridian.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            origin TEXT,
            description TEXT,
            storage_reqs TEXT,
            security_level TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE climate_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            reading TEXT,
            sensor_type TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE global_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_name TEXT,
            config_value TEXT
        )
    ''')

    # Seed Data
    cursor.execute("INSERT INTO inventory_items (name, origin, description, storage_reqs, security_level) VALUES (?, ?, ?, ?, ?)", 
                   ('Ming Dynasty Vase', 'China', 'Exquisite blue and white porcelain.', 'Temp: 22C, Humidity: 45%', 'High'))
    cursor.execute("INSERT INTO inventory_items (name, origin, description, storage_reqs, security_level) VALUES (?, ?, ?, ?, ?)", 
                   ('Lunar Regolith Sample', 'Moon (Apollo 17)', 'Original container 784-A.', 'Vacuum Seal, Low Gravity Sim', 'Restricted'))
    cursor.execute("INSERT INTO inventory_items (name, origin, description, storage_reqs, security_level) VALUES (?, ?, ?, ?, ?)", 
                   ('Voynich Manuscript', 'Europe', 'Undeciphered botanical document.', 'Dim lighting, Argon purge', 'Ultra'))

    cursor.execute("INSERT INTO facilities (location) VALUES ('Geneva Free Port'), ('Singapore Secure Vault'), ('Kentucky Logistics Hub')")

    cursor.execute("INSERT INTO climate_logs (facility_id, reading, sensor_type) VALUES (1, '21.5C', 'Temperature'), (1, '44.2%', 'Humidity'), (2, '18.1C', 'Temperature')")

    # Read flag from /flag.txt (only available during build)
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{LOCAL_TEST_FLAG}"

    cursor.execute("INSERT INTO global_config (config_name, config_value) VALUES ('system_version', '4.2.1')")
    cursor.execute("INSERT INTO global_config (config_name, config_value) VALUES ('master_vault_token', ?)", (flag,))
    cursor.execute("INSERT INTO global_config (config_name, config_value) VALUES ('maintenance_mode', 'false')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()