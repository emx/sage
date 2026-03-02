import sqlite3
import os

def init():
    db_path = 'aetherlink.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        display_filter TEXT
    )''')
    
    # Telemetry logs table
    c.execute('''CREATE TABLE telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        satellite_id TEXT,
        sensor_data TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Obfuscated vault table for flag
    c.execute('''CREATE TABLE system_vault (
        id INTEGER PRIMARY KEY,
        vault_key TEXT,
        secret_key TEXT,
        vault_data TEXT
    )''')
    
    # Insert users
    c.execute("INSERT INTO users (username, password, display_filter) VALUES ('admin', 'redacted_super_secret', '1=1')")
    c.execute("INSERT INTO users (username, password, display_filter) VALUES ('guest', 'guest123', '1=1')")
    
    # Insert telemetry data
    logs = [
        ('HORIZON-1', 'Battery Volt: 3.7V | Temp: -40C'),
        ('HORIZON-1', 'Attitude Adjustment: Success | Gyro: Stable'),
        ('HORIZON-1', 'Solar Panel Deploy: 100% | Power: 450W'),
        ('HORIZON-1', 'Uplink Synced | Bitrate: 1.2 Gbps')
    ]
    for log in logs:
        c.execute("INSERT INTO telemetry_logs (satellite_id, sensor_data) VALUES (?, ?)", log)
        
    # Insert flag into the obfuscated table
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO system_vault (vault_key, secret_key, vault_data) VALUES (?, ?, ?)", 
              ('AetherLink-7-Master', 'SAT_ENCRYPTION_KEY', flag))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()