import sqlite3
import os

def init():
    db_path = '/app/logistics.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Manifests table
    c.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY,
        origin TEXT, 
        destination TEXT, 
        status TEXT, 
        coordinator_id INTEGER
    )''')
    
    # Telemetry table
    c.execute('''CREATE TABLE telemetry (
        id INTEGER PRIMARY KEY,
        manifest_id INTEGER,
        container_id TEXT,
        temperature REAL,
        humidity REAL,
        pressure REAL
    )''')

    # Hidden system table
    c.execute('''CREATE TABLE internal_system_settings (
        id INTEGER PRIMARY KEY,
        setting_key TEXT,
        setting_value TEXT
    )''')

    # Seed data
    c.execute("INSERT INTO manifests VALUES (1, 'Singapore Hub', 'Rotterdam Port', 'In Transit', 104)")
    c.execute("INSERT INTO manifests VALUES (2, 'Port of Long Beach', 'Tokyo Hub', 'Processing', 105)")

    # Specific telemetry data to make sorting obvious for boolean oracle
    # Temperature: 10, 20, 30 | Humidity: 40, 50, 60
    c.execute("INSERT INTO telemetry VALUES (1, 1, 'CONT-A01', 10.5, 60.1, 1013)")
    c.execute("INSERT INTO telemetry VALUES (2, 1, 'CONT-B02', 20.2, 50.4, 1012)")
    c.execute("INSERT INTO telemetry VALUES (3, 1, 'CONT-C03', 30.8, 40.2, 1014)")

    # Load flag from file and insert into hidden table
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO internal_system_settings (setting_key, setting_value) VALUES ('master_encryption_key', ?)", (flag,))
    c.execute("INSERT INTO internal_system_settings (setting_key, setting_value) VALUES ('api_backup_node', 'https://backup-logistics.velocestream.internal/v1')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()