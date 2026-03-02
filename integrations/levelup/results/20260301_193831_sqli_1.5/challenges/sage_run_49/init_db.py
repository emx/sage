import sqlite3
import os

def init():
    db_path = 'verdant_logix.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute('CREATE TABLE freight_manifests (id INTEGER PRIMARY KEY, container_id TEXT, origin TEXT, destination TEXT, priority TEXT)')
    cursor.execute('CREATE TABLE vehicle_telemetry (id INTEGER PRIMARY KEY, vehicle_id TEXT, timestamp TEXT, lat REAL, lon REAL, speed INTEGER)')
    cursor.execute('CREATE TABLE network_nodes (id INTEGER PRIMARY KEY, node_name TEXT, status TEXT, last_ping TEXT)')
    cursor.execute('CREATE TABLE system_configs (id INTEGER PRIMARY KEY, key TEXT, value TEXT)')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password) VALUES ('supervisor_alpha', 'vlogix_2024_secure_pass')")
    
    manifests = [
        ('CNTR-9902', 'Port of Rotterdam', 'Berlin Hub', 'High'),
        ('CNTR-1142', 'Shanghai Terminal', 'Los Angeles Port', 'Medium'),
        ('CNTR-5531', 'Hamburg Logistics', 'Prague Depot', 'Low'),
        ('CNTR-8820', 'Singapore Gateway', 'Sydney Port', 'High')
    ]
    cursor.executemany('INSERT INTO freight_manifests (container_id, origin, destination, priority) VALUES (?, ?, ?, ?)', manifests)
    
    telemetry = [
        ('TRUCK-V102', '2024-05-20 10:15:00', 52.5200, 13.4050, 85),
        ('SHIP-M004', '2024-05-20 10:14:22', 31.2304, 121.4737, 22),
        ('TRUCK-V220', '2024-05-20 10:12:05', 48.8566, 2.3522, 0)
    ]
    cursor.executemany('INSERT INTO vehicle_telemetry (vehicle_id, timestamp, lat, lon, speed) VALUES (?, ?, ?, ?, ?)', telemetry)
    
    nodes = [
        ('FRA-01-HUB', 'ONLINE', '2 mins ago'),
        ('LHR-04-GATE', 'ONLINE', '1 min ago'),
        ('SIN-09-NODE', 'ONLINE', '5 mins ago'),
        ('NYC-02-CENTRAL', 'ONLINE', '30 secs ago')
    ]
    cursor.executemany('INSERT INTO network_nodes (node_name, status, last_ping) VALUES (?, ?, ?)', nodes)

    # Flag insertion
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{PLACEHOLDER_FLAG}"
    
    cursor.execute("INSERT INTO system_configs (key, value) VALUES ('master_access_key', ?)", (flag,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()