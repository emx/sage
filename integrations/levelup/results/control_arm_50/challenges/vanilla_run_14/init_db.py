import sqlite3
import os

def init():
    db_path = '/tmp/verdant_analytics.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create standard tables
    cursor.execute('''CREATE TABLE regions (id INTEGER PRIMARY KEY, name TEXT, climate TEXT)''')
    cursor.execute('''CREATE TABLE sensor_readings (id INTEGER PRIMARY KEY, sensor_name TEXT, region_id INTEGER, humidity REAL, temperature REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create obfuscated internal table
    cursor.execute('''CREATE TABLE internal_system_config (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')

    # Seed Data
    cursor.execute("INSERT INTO regions (name, climate) VALUES ('North Plateau', 'Temperate'), ('South Basin', 'Arid'), ('Eastern Delta', 'Tropical')")
    cursor.execute("INSERT INTO sensor_readings (sensor_name, region_id, humidity, temperature) VALUES ('S-101', 1, 45.2, 22.1), ('S-102', 1, 44.8, 22.5), ('S-201', 2, 12.5, 35.8), ('S-301', 3, 88.2, 28.4)")
    
    # Insert flag from root-only file
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO internal_system_config (config_key, config_value) VALUES ('system_api_secret', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO internal_system_config (config_key, config_value) VALUES ('system_api_secret', 'ERROR: FLAG_NOT_FOUND')")

    cursor.execute("INSERT INTO internal_system_config (config_key, config_value) VALUES ('maintenance_window', 'Sunday 02:00 UTC'), ('log_retention_days', '90')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()