import sqlite3
import os

DB_PATH = '/tmp/aetheria.db'

def init():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'p@ssw0rd_very_secret_9921', 'administrator')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest_aetheria_2024', 'auditor')")

    # Manifests table
    cursor.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY, 
        tracking_number TEXT, 
        vessel_name TEXT, 
        origin_port TEXT, 
        cargo_type TEXT, 
        status TEXT
    )''')
    
    manifest_data = [
        ('AE-99210', 'The Northern Star', 'Singapore', 'Electronics', 'In Transit'),
        ('AE-44122', 'Oceanic Voyager', 'Rotterdam', 'Heavy Machinery', 'Pending'),
        ('AE-10029', 'Aetheria Pride', 'Dubai', 'Textiles', 'Delivered'),
        ('AE-88211', 'Global Express', 'Shanghai', 'Medical Supplies', 'Customs Check'),
        ('AE-33490', 'Horizon Spirit', 'Los Angeles', 'Automotive Parts', 'Departed')
    ]
    cursor.executemany('INSERT INTO manifests (tracking_number, vessel_name, origin_port, cargo_type, status) VALUES (?,?,?,?,?)', manifest_data)

    # Hidden table for flag
    cursor.execute('CREATE TABLE internal_routing_config (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag}"
        
    cursor.execute("INSERT INTO internal_routing_config (config_key, config_value) VALUES ('emergency_override_secret', ?)", (flag,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()