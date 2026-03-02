import sqlite3
import os

def initialize():
    # The DB will be created in /tmp during runtime, but we save a template in /app
    db_path = '/app/vanguard_logistics.db.bak'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE manifests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            cargo_type TEXT NOT NULL,
            priority INTEGER
        );

        CREATE TABLE fleet_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vessel_id INTEGER NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE vanguard_system_meta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT NOT NULL,
            config_value TEXT NOT NULL
        );
    ''')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'viewer')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'VanguardSuperAdmin2024!', 'admin')")

    cursor.execute("INSERT INTO manifests (tracking_number, origin, destination, cargo_type, priority) VALUES ('VML-9928', 'Port of Singapore', 'Rotterdam', 'Industrial Electronics', 1)")
    cursor.execute("INSERT INTO manifests (tracking_number, origin, destination, cargo_type, priority) VALUES ('VML-4412', 'Shanghai', 'Long Beach', 'Consumer Goods', 2)")
    cursor.execute("INSERT INTO manifests (tracking_number, origin, destination, cargo_type, priority) VALUES ('VML-1002', 'Hamburg', 'Dubai', 'Hazardous Chemicals', 1)")

    cursor.execute("INSERT INTO fleet_telemetry (vessel_id, status) VALUES (1, 'active')")
    cursor.execute("INSERT INTO fleet_telemetry (vessel_id, status) VALUES (2, 'maintenance')")

    # Flag insertion
    flag = "LEVELUP{pzocrVKbutCaS2UAbcM0GpsDH1B3SbpO}"
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        pass

    cursor.execute("INSERT INTO vanguard_system_meta (config_key, config_value) VALUES ('api_version', 'v1.4.2')")
    cursor.execute("INSERT INTO vanguard_system_meta (config_key, config_value) VALUES ('system_integrity_hash', ?)", (flag,))
    
    conn.commit()
    conn.close()
    # Also copy to /tmp for immediate availability during docker build testing if needed
    try:
        import shutil
        shutil.copy(db_path, '/tmp/vanguard_logistics.db')
    except:
        pass

if __name__ == '__main__':
    initialize()