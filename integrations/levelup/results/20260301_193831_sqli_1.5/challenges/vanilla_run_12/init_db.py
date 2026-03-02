import sqlite3
import os

def init():
    db_path = "/tmp/velogreen.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Business data
    c.execute('CREATE TABLE plots (id INTEGER PRIMARY KEY, name TEXT, coordinates TEXT, soil_type TEXT)')
    c.execute('INSERT INTO plots VALUES (1, "North Sector A1", "45.523,-122.676", "Silt Loam")')
    c.execute('INSERT INTO plots VALUES (2, "East Valley G4", "45.512,-122.641", "Clay")')
    c.execute('INSERT INTO plots VALUES (3, "Riverside B9", "45.505,-122.690", "Sandy Loam")')

    c.execute('CREATE TABLE sensor_logs (id INTEGER PRIMARY KEY, sensor_id TEXT, temperature REAL, status TEXT, timestamp TEXT)')
    c.execute('INSERT INTO sensor_logs VALUES (101, "SN-9920", 21.4, "ONLINE", "2024-05-01 10:00:00")')
    c.execute('INSERT INTO sensor_logs VALUES (102, "SN-9921", 19.8, "ONLINE", "2024-05-01 10:05:00")')
    c.execute('INSERT INTO sensor_logs VALUES (103, "SN-9844", 22.1, "ONLINE", "2024-05-01 10:10:00")')
    c.execute('INSERT INTO sensor_logs VALUES (104, "SN-9920", 21.5, "ONLINE", "2024-05-01 10:15:00")')

    # Flag data (obfuscated)
    c.execute('CREATE TABLE internal_metadata (id INTEGER PRIMARY KEY, entry_key TEXT, entry_value TEXT)')
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder}"
    
    c.execute('INSERT INTO internal_metadata (entry_key, entry_value) VALUES ("system_init_vector", "7e8221bc3")')
    c.execute('INSERT INTO internal_metadata (entry_key, entry_value) VALUES ("flag_token", ?)', (flag,))
    c.execute('INSERT INTO internal_metadata (entry_key, entry_value) VALUES ("api_secret_fallback", "dGhpcyBpcyBub3QgdGhlIGZsYWc=")')

    conn.commit()
    conn.close()
    os.chmod(db_path, 0o666)

if __name__ == "__main__":
    init()