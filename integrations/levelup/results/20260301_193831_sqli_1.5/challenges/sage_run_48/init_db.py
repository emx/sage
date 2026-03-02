import sqlite3
import os

def init():
    db_path = '/app/data.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE coordinators (id INTEGER PRIMARY KEY, username TEXT, auth_token TEXT, region TEXT, role TEXT)''')
    c.execute('''CREATE TABLE manifests (id INTEGER PRIMARY KEY, item TEXT, origin TEXT, destination TEXT, status TEXT)''')
    c.execute('''CREATE TABLE telemetry (id INTEGER PRIMARY KEY, silo_name TEXT, fill_level INTEGER, temperature REAL)''')
    c.execute('''CREATE TABLE site_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)''')
    
    # Seed Data
    c.execute("INSERT INTO coordinators (username, auth_token, region, role) VALUES ('admin', 'AETHER_ADM_9921', 'Central Command', 'Regional Overseer')")
    c.execute("INSERT INTO coordinators (username, auth_token, region, role) VALUES ('jdoe', 'NORTH_COORD_12', 'Northern Plains', 'Field Manager')")
    
    c.execute("INSERT INTO manifests (item, origin, destination, status) VALUES ('Winter Wheat', 'Silo-7', 'Port Central', 'In Transit')")
    c.execute("INSERT INTO manifests (item, origin, destination, status) VALUES ('Golden Corn', 'Silo-3', 'Regional Mill', 'Delivered')")
    c.execute("INSERT INTO manifests (item, origin, destination, status) VALUES ('Organic Soy', 'Silo-12', 'Port Central', 'Pending')")
    
    c.execute("INSERT INTO telemetry (silo_name, fill_level, temperature) VALUES ('Silo Alpha-1', 85, 18.5)")
    c.execute("INSERT INTO telemetry (silo_name, fill_level, temperature) VALUES ('Silo Beta-4', 42, 21.2)")
    
    c.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('portal_theme', 'corporate_blue')")
    
    # The Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('emergency_canary', ?)", (flag,))
    except:
        c.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('emergency_canary', 'LEVELUP{PLACEHOLDER}')")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()