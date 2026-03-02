import sqlite3
import os

def init():
    db = sqlite3.connect('/tmp/verdant.db')
    cursor = db.cursor()

    # Users table
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '" + os.urandom(16).hex() + "')")
    cursor.execute("INSERT INTO users (username, password) VALUES ('guest', 'guest123')")

    # Soil Metrics
    cursor.execute('CREATE TABLE soil_metrics (id INTEGER PRIMARY KEY, region TEXT, n_level INTEGER, p_level INTEGER, k_level INTEGER)')
    regions = ['North', 'South', 'East', 'West', 'Central', 'Coastal']
    for i in range(1, 101):
        cursor.execute("INSERT INTO soil_metrics (region, n_level, p_level, k_level) VALUES (?, ?, ?, ?)", 
                       (regions[i % 6], 40 + (i % 20), 15 + (i % 10), 100 + (i % 50)))

    # Saved Regions (Second Order Table)
    cursor.execute('CREATE TABLE saved_regions (id INTEGER PRIMARY KEY, user_id INTEGER, region_name TEXT)')
    
    # Site Settings (Obfuscated Flag Storage)
    cursor.execute('CREATE TABLE site_settings (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')
    
    # Read flag and insert
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{PLACEHOLDER_FLAG}"
        
    cursor.execute("INSERT INTO site_settings (config_key, config_value) VALUES (?, ?)", ('vault_recovery_key', flag))
    cursor.execute("INSERT INTO site_settings (config_key, config_value) VALUES (?, ?)", ('system_version', 'v4.2.1-stable'))
    cursor.execute("INSERT INTO site_settings (config_key, config_value) VALUES (?, ?)", ('api_endpoint', 'https://api.internal.vpulse.com'))

    db.commit()
    db.close()
    
    # Ensure DB is readable/writable by the runtime user
    os.chmod('/tmp/verdant.db', 0o666)

if __name__ == '__main__':
    init()