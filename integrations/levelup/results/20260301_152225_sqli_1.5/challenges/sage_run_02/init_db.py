import sqlite3
import os

def init():
    db_path = '/tmp/aetherlink.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, email TEXT)')
    c.execute('CREATE TABLE satellites (id INTEGER PRIMARY KEY, name TEXT, serial_number TEXT, orbit TEXT)')
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, item_name TEXT, weight REAL, destination TEXT)')
    c.execute('CREATE TABLE telemetry (id INTEGER PRIMARY KEY, sat_id INTEGER, sensor TEXT, value TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE maintenance_logs (id INTEGER PRIMARY KEY, technician TEXT, note TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE site_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)')

    # Users
    c.execute("INSERT INTO users VALUES (1, 'admin', 'SuperSecretAdmin2024!', 'administrator', 'admin@aetherlink.io')")
    c.execute("INSERT INTO users VALUES (2, 's.ross', 'techpass1', 'technician', 's.ross@aetherlink.io')")
    c.execute("INSERT INTO users VALUES (3, 'guest', 'guest123', 'viewer', 'guest@aetherlink.io')")

    # Satellites
    c.execute("INSERT INTO satellites VALUES (1, 'Aether-7 Global Comm', 'AL-7700-X', 'GEO')")
    c.execute("INSERT INTO satellites VALUES (2, 'StarMap Imaging', 'SMI-12-B', 'LEO')")
    c.execute("INSERT INTO satellites VALUES (3, 'DeepSpace Relay', 'DSR-09-V', 'MEO')")

    # Manifests
    c.execute("INSERT INTO manifests VALUES (1, 'Ion Thruster Module', 450.5, 'LEO Orbit')")
    c.execute("INSERT INTO manifests VALUES (2, 'Solar Array Panel A', 120.0, 'GEO Orbit')")
    c.execute("INSERT INTO manifests VALUES (3, 'K-Band Transponder', 15.2, 'MEO Orbit')")

    # Telemetry
    for i in range(10):
        c.execute(f"INSERT INTO telemetry (sat_id, sensor, value) VALUES (1, 'Thermal-Core', '{20+i}.5 C')")
        c.execute(f"INSERT INTO telemetry (sat_id, sensor, value) VALUES (1, 'Power-Draw', '{1200+i*10} W')")

    # Logs
    c.execute("INSERT INTO maintenance_logs (technician, note) VALUES ('s.ross', 'Initial diagnostic of K-Band antenna complete. No issues found.')")
    c.execute("INSERT INTO maintenance_logs (technician, note) VALUES ('m.chen', 'Calibration of the StarMap imaging sensor scheduled for next Tuesday.')")

    # Flag insertion (from /flag.txt)
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('enc_root_passphrase', ?)", (flag,))
    except Exception as e:
        print(f"Error reading flag: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()