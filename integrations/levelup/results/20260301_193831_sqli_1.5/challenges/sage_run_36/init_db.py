import sqlite3
import os

def init():
    db_path = '/tmp/aether.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'Th3_Gr3at_A3th3r_2024!', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('dispatcher_beta', 'AetherDispatch2024!', 'user')")

    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, tracking_number TEXT, cargo_type TEXT, destination TEXT, valuation INTEGER)')
    manifest_data = [
        ('AE-9001', 'High-Value Electronics', 'Tokyo, JP', 450000),
        ('AE-4421', 'Medical Supplies', 'Berlin, DE', 120000),
        ('AE-1029', 'Agricultural Tech', 'Nairobi, KE', 85000),
        ('AE-7782', 'Aviation Parts', 'Seattle, US', 890000),
        ('AE-3310', 'Industrial Robotics', 'Seoul, KR', 1200000)
    ]
    c.executemany('INSERT INTO manifests (tracking_number, cargo_type, destination, valuation) VALUES (?, ?, ?, ?)', manifest_data)

    c.execute('CREATE TABLE drivers (id INTEGER PRIMARY KEY, name TEXT, badge_id TEXT, clearance_level INTEGER)')
    drivers = [
        ('Robert Miller', 'B-112', 2),
        ('Sarah Jenkins', 'B-509', 3),
        ('Michael Chen', 'B-221', 2)
    ]
    c.executemany('INSERT INTO drivers (name, badge_id, clearance_level) VALUES (?, ?, ?)', drivers)

    # Obfuscated Flag Table
    c.execute('CREATE TABLE internal_assets_metadata (id INTEGER PRIMARY KEY, asset_key TEXT, asset_value TEXT)')
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    c.execute("INSERT INTO internal_assets_metadata (asset_key, asset_value) VALUES ('system_flag', ?)", (flag,))
    c.execute("INSERT INTO internal_assets_metadata (asset_key, asset_value) VALUES ('db_version', 'sqlite-3.45.0')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()