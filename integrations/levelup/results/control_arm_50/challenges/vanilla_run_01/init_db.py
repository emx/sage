import sqlite3
import os

def init():
    db_path = '/tmp/velovista.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    c.execute("INSERT INTO users VALUES (1, 'admin', 'VeloAdmin2024!', 'administrator')")
    c.execute("INSERT INTO users VALUES (2, 'guest', 'guest', 'auditor')")

    c.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_id TEXT, destination TEXT, weight INTEGER, status TEXT)''')
    shipments = [
        (1, 'VV-TRK-9001', 'Berlin, DE', 450, 'In Transit'),
        (2, 'VV-TRK-1024', 'Tokyo, JP', 1200, 'Pending'),
        (3, 'VV-TRK-4452', 'London, UK', 320, 'Delivered'),
        (4, 'VV-TRK-8819', 'New York, US', 2100, 'Processing'),
        (5, 'VV-TRK-5561', 'Singapore, SG', 890, 'Customs')
    ]
    c.executemany("INSERT INTO shipments VALUES (?, ?, ?, ?, ?)", shipments)

    c.execute('''CREATE TABLE vehicles (id INTEGER PRIMARY KEY, vin TEXT, model TEXT, driver TEXT)''')
    vehicles = [
        (1, '1V9BV11X0', 'Freightliner Cascadia', 'Mark S.'),
        (2, '3V2GV44Z1', 'Volvo VNL 860', 'Sarah L.'),
        (3, '5V7HV22Y9', 'Tesla Semi', 'Autonomous Unit 04')
    ]
    c.executemany("INSERT INTO vehicles VALUES (?, ?, ?, ?)", vehicles)

    # Obfuscated flag table
    c.execute('''CREATE TABLE app_internal_registry (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')
    c.execute("INSERT INTO app_internal_registry (config_key, config_value) VALUES ('ui.theme.primary', '#2c3e50')")
    c.execute("INSERT INTO app_internal_registry (config_key, config_value) VALUES ('api.timeout_ms', '5000')")
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO app_internal_registry (config_key, config_value) VALUES ('system.internal.node_id', ?)", (flag,))
    except:
        c.execute("INSERT INTO app_internal_registry (config_key, config_value) VALUES ('system.internal.node_id', 'LEVELUP{DEBUG_FLAG}')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()