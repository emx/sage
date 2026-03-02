import sqlite3
import os

def init():
    db_path = '/tmp/vanguard.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE manifests (id INTEGER PRIMARY KEY, cargo_id TEXT, destination TEXT, status TEXT, weight INTEGER)''')
    cursor.execute('''CREATE TABLE drones (id INTEGER PRIMARY KEY, drone_name TEXT, battery INTEGER, depth INTEGER, status TEXT)''')
    cursor.execute('''CREATE TABLE telemetry_logs (id INTEGER PRIMARY KEY, drone_id INTEGER, timestamp TEXT, message TEXT)''')
    cursor.execute('''CREATE TABLE system_node_metadata (id INTEGER PRIMARY KEY, node_name TEXT, node_auth_token TEXT)''')

    # Seed data
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'VanguardSuperSecretAdmin2024!', 'admin')")
    cursor.execute("INSERT INTO users VALUES (2, 'guest', 'vanguard2024', 'user')")

    cursor.execute("INSERT INTO manifests VALUES (1, 'CX-900', 'Bermuda Triangle Hub', 'In Transit', 4500)")
    cursor.execute("INSERT INTO manifests VALUES (2, 'CX-901', 'Arctic Research Station', 'Delivered', 1200)")
    cursor.execute("INSERT INTO manifests VALUES (3, 'CX-905', 'Mariana Trench Lab', 'Preparing', 800)")

    cursor.execute("INSERT INTO drones VALUES (1, 'Kraken-1', 88, 4500, 'Active')")
    cursor.execute("INSERT INTO drones VALUES (2, 'Leviathan-4', 42, 8900, 'Low Power')")

    cursor.execute("INSERT INTO telemetry_logs VALUES (1, 1, '2023-10-01 12:00:01', 'System initialization complete.')")
    cursor.execute("INSERT INTO telemetry_logs VALUES (2, 1, '2023-10-01 12:05:00', 'Descent to 1000m reached.')")
    cursor.execute("INSERT INTO telemetry_logs VALUES (3, 1, '2023-10-01 12:10:45', 'Obstacle detected and bypassed.')")

    # Insert flag into obfuscated table
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    cursor.execute("INSERT INTO system_node_metadata (node_name, node_auth_token) VALUES ('Global_API_Gateway', ?)", (flag,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()