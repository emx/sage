import sqlite3
import os

DB_PATH = '/tmp/verdant.db'

def init():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute("INSERT INTO users VALUES (1, 'agri_manager', 'greenhouse2024', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'guest', 'guest2024', 'viewer')")

    c.execute('CREATE TABLE field_settings (id INTEGER PRIMARY KEY, field_name TEXT, crop_type TEXT, sort_pref TEXT)')
    c.execute("INSERT INTO field_settings VALUES (1, 'North Plot', 'Soybeans', 'timestamp')")
    c.execute("INSERT INTO field_settings VALUES (2, 'East Ridge', 'Maize', 'timestamp')")
    c.execute("INSERT INTO field_settings VALUES (3, 'South Valley', 'Wheat', 'timestamp')")

    c.execute('CREATE TABLE sensor_logs (id INTEGER PRIMARY KEY, field_id INTEGER, ph_level REAL, nitrogen INTEGER, timestamp TEXT)')
    # Data designed for sorting oracle: PH is high when Nitrogen is low, and vice versa
    logs = [
        (1, 4.5, 250, '2023-10-01 08:00'),
        (1, 8.2, 10, '2023-10-01 09:00'),
        (1, 6.0, 100, '2023-10-01 10:00'),
        (2, 5.5, 120, '2023-10-01 08:30'),
        (3, 7.1, 45, '2023-10-01 08:45')
    ]
    c.executemany('INSERT INTO sensor_logs (field_id, ph_level, nitrogen, timestamp) VALUES (?,?,?,?)', logs)

    c.execute('CREATE TABLE site_config (id INTEGER PRIMARY KEY, cat_key TEXT, cat_val TEXT)')
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    c.execute("INSERT INTO site_config (cat_key, cat_val) VALUES ('sys.auth.entropy_seed', ?)", (flag,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()