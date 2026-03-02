import sqlite3
import os

DB_PATH = "/tmp/verdant.db"
FLAG_PATH = "/flag.txt"

def init():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Manifests table
    c.execute('''CREATE TABLE manifests (id INTEGER PRIMARY KEY, origin TEXT, destination TEXT, weight INTEGER, status TEXT)''')
    c.executemany("INSERT INTO manifests VALUES (?,?,?,?,?)", [
        (101, 'Atlanta, GA', 'Seattle, WA', 4500, 'In Transit'),
        (102, 'Miami, FL', 'Chicago, IL', 2100, 'Delivered'),
        (103, 'Austin, TX', 'New York, NY', 3300, 'Pending'),
        (104, 'Denver, CO', 'Los Angeles, CA', 1200, 'In Transit'),
        (105, 'Boston, MA', 'Dallas, TX', 5600, 'Processing')
    ])

    # Drivers table
    c.execute('''CREATE TABLE drivers (id INTEGER PRIMARY KEY, emp_id TEXT, name TEXT, grade TEXT, compliance INTEGER)''')
    c.executemany("INSERT INTO drivers VALUES (?,?,?,?,?)", [
        (1, 'VP-8821', 'James Henderson', 'A+', 98),
        (2, 'VP-1029', 'Sarah Jenkins', 'B', 85),
        (3, 'VP-4492', 'Robert Miller', 'A', 92)
    ])

    # Maintenance table
    c.execute('''CREATE TABLE maintenance_logs (id INTEGER PRIMARY KEY, vin TEXT, date TEXT, action TEXT, tech TEXT)''')
    c.executemany("INSERT INTO maintenance_logs VALUES (?,?,?,?,?)", [
        (1, '1V9HG2...', '2024-01-15', 'Oil Change', 'T. Stark'),
        (2, '2G4NF9...', '2024-02-01', 'Brake Inspection', 'S. Rogers')
    ])

    # Obfuscated Config table containing the flag
    c.execute('''CREATE TABLE app_config (config_id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')
    
    flag = "LEVELUP{ERROR_LOADING_FLAG}"
    try:
        with open(FLAG_PATH, 'r') as f:
            flag = f.read().strip()
    except:
        pass

    c.execute("INSERT INTO app_config (config_key, config_value) VALUES (?, ?)", ('internal_secret_key', flag))
    c.execute("INSERT INTO app_config (config_key, config_value) VALUES (?, ?)", ('analytics_tracking_id', 'UA-9921044-1'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()