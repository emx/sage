import sqlite3
import os

def init():
    db_path = 'veridian.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute('INSERT INTO users (username, password, role) VALUES ("admin", "super_secret_vks_2024", "administrator")')
    c.execute('INSERT INTO users (username, password, role) VALUES ("coordinator_01", "shipping123", "user")')
    
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, manifest_id TEXT, destination TEXT, priority TEXT, status TEXT)')
    manifests = [
        ('M-9921', 'London Heathrow', 'High', 'In-Transit'),
        ('M-1024', 'Tokyo Narita', 'Standard', 'Docked'),
        ('M-5582', 'New York JFK', 'Urgent', 'Processing'),
        ('M-3310', 'Singapore Changi', 'Low', 'Delivered')
    ]
    c.executemany('INSERT INTO manifests (manifest_id, destination, priority, status) VALUES (?,?,?,?)', manifests)
    
    c.execute('CREATE TABLE fleet_assets (id INTEGER PRIMARY KEY, asset_name TEXT, asset_type TEXT, location TEXT)')
    ships = [
        ('VK-Titan', 'Heavy Lifter', 'North Atlantic'),
        ('VK-Swift', 'Express Courier', 'Pacific Rim'),
        ('VK-Carrier-01', 'Bulk Carrier', 'Indian Ocean')
    ]
    c.executemany('INSERT INTO fleet_assets (asset_name, asset_type, location) VALUES (?,?,?)', ships)

    c.execute('CREATE TABLE telemetry_units (id INTEGER PRIMARY KEY, unit_id TEXT, status TEXT)')
    units = [
        ('101', 'Nominal: Voltage Stable'),
        ('102', 'Alert: Cooling system bypass'),
        ('201', 'Maintenance Required'),
        ('404', 'Unit Offline')
    ]
    c.executemany('INSERT INTO telemetry_units (unit_id, status) VALUES (?,?)', units)

    # Obfuscated Flag Table
    c.execute('CREATE TABLE internal_vault (id INTEGER PRIMARY KEY, secret_key TEXT, secret_value TEXT)')
    flag = open('/flag.txt', 'r').read().strip()
    c.execute('INSERT INTO internal_vault (secret_key, secret_value) VALUES ("system_integrity_hash", ?)', (flag,))
    c.execute('INSERT INTO internal_vault (secret_key, secret_value) VALUES ("master_api_key", "vks_77821_legacy_auth")')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()