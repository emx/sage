import sqlite3
import random
import os

def init():
    db_path = '/tmp/vanguard.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('CREATE TABLE satellites (id INTEGER PRIMARY KEY, name TEXT, status TEXT, orbit TEXT)')
    c.execute('CREATE TABLE telemetry_logs (id INTEGER PRIMARY KEY, satellite_id INTEGER, timestamp DATETIME, fuel_level REAL, signal_strength INTEGER)')
    # Obfuscated internal table to prevent simple guessing
    c.execute('CREATE TABLE _vanguard_internal_vault_6472 (item_id INTEGER PRIMARY KEY, item_key TEXT, item_value TEXT)')

    sats = [
        (1, 'Aether-1', 'Active', 'LEO'),
        (2, 'Aether-2', 'Maintenance', 'GEO'),
        (3, 'Vanguard-Prime', 'Active', 'MEO'),
        (4, 'Sentinel-X', 'Decommissioned', 'LEO')
    ]
    c.executemany('INSERT INTO satellites VALUES (?,?,?,?)', sats)

    for i in range(100):
        c.execute('INSERT INTO telemetry_logs (satellite_id, timestamp, fuel_level, signal_strength) VALUES (?, datetime("now",?), ?, ?)',
                  (random.randint(1,4), f'-{i} minutes', random.uniform(10, 95), random.randint(30, 99)))

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{LOCAL_TEST_FLAG}"
    
    c.execute('INSERT INTO _vanguard_internal_vault_6472 (item_key, item_value) VALUES (?, ?)', 
              ('VANGUARD_CORE_TOKEN', flag))
    c.execute('INSERT INTO _vanguard_internal_vault_6472 (item_key, item_value) VALUES (?, ?)', 
              ('MAINTENANCE_ID_PREFIX', 'Vanguard-MT-2024'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()