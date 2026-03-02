import sqlite3
import os

def init():
    db_path = '/tmp/aetheron.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT INTO users VALUES (1, 'engineer', 'aetheron2024')")

    c.execute('''CREATE TABLE components (id INTEGER PRIMARY KEY, serial_number TEXT, model TEXT, status TEXT)''')
    c.execute("INSERT INTO components VALUES (1, 'SN-001-A', 'StarTracker L1', 'Operational')")
    c.execute("INSERT INTO components VALUES (2, 'SN-442-B', 'GyroScope G2', 'Maintenance')")
    c.execute("INSERT INTO components VALUES (3, 'SN-109-L', 'Legacy TempSensor', 'Operational')")

    c.execute('''CREATE TABLE telemetry (id INTEGER PRIMARY KEY, satellite_name TEXT, timestamp TEXT, reading_type TEXT, value TEXT)''')
    c.execute("INSERT INTO telemetry VALUES (1, 'Aether-1', '2024-05-20 10:00:01', 'Solar Voltage', '32.4V')")
    c.execute("INSERT INTO telemetry VALUES (2, 'Aether-1', '2024-05-20 10:00:05', 'CPU Temp', '45.2C')")
    c.execute("INSERT INTO telemetry VALUES (3, 'Aether-2', '2024-05-20 10:01:22', 'Inertial Alignment', '0.002')")

    # Obfuscated table for flag
    c.execute('''CREATE TABLE internal_assets (id INTEGER PRIMARY KEY, asset_tag TEXT, content TEXT)''')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO internal_assets (asset_tag, content) VALUES ('MISSION_FLAG', ?)", (flag,))
    except:
        c.execute("INSERT INTO internal_assets (asset_tag, content) VALUES ('MISSION_FLAG', 'LEVELUP{PLACEHOLDER_IF_FILE_MISSING}')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()