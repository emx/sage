import sqlite3
import os

def init_db():
    db_path = '/tmp/verdant.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('''CREATE TABLE manifests (id INTEGER PRIMARY KEY, tracking_no TEXT, origin TEXT, destination TEXT, status TEXT)''')
    c.execute('''CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, registry TEXT, capacity TEXT)''')
    c.execute('''CREATE TABLE telemetry_logs (id INTEGER PRIMARY KEY, vessel_id INTEGER, timestamp TEXT, temp_c REAL, humidity REAL)''')
    c.execute('''CREATE TABLE system_audit_config (record_id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')

    # Seed Data
    c.execute("INSERT INTO manifests VALUES (1, 'VPL-99281', 'Rotterdam, NL', 'Singapore, SG', 'In Transit')")
    c.execute("INSERT INTO manifests VALUES (2, 'VPL-10293', 'Shanghai, CN', 'Los Angeles, US', 'Processing')")
    
    c.execute("INSERT INTO vessels VALUES (1, 'Verdant Voyager', 'Marshall Islands', '18,000 TEU')")
    c.execute("INSERT INTO vessels VALUES (2, 'Emerald Explorer', 'Panama', '15,500 TEU')")

    # Telemetry data for vessel 1
    telemetry_data = [
        (1, '2023-11-01 10:00:00', 4.2, 85.1),
        (1, '2023-11-01 11:00:00', 4.5, 84.8),
        (1, '2023-11-01 12:00:00', 3.9, 86.2),
        (1, '2023-11-01 13:00:00', 4.1, 85.5),
    ]
    c.executemany("INSERT INTO telemetry_logs (vessel_id, timestamp, temp_c, humidity) VALUES (?, ?, ?, ?)", telemetry_data)

    # Flag insertion from /flag.txt
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO system_audit_config (config_key, config_value) VALUES ('emergency_override_token', ?)", (flag,))
    except FileNotFoundError:
        pass

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()