import sqlite3
import os

def init():
    DB_PATH = '/tmp/orbit_logistics.db'
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY,
        container_id TEXT NOT NULL,
        origin TEXT,
        destination TEXT,
        weight INTEGER,
        status TEXT
    )''')

    cursor.execute('''CREATE TABLE system_health_checks (
        id INTEGER PRIMARY KEY,
        service_name TEXT NOT NULL,
        health_token TEXT NOT NULL,
        last_ping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Seed Manifest Data
    manifests = [
        ('OSL-1122-3344', 'Shanghai, CN', 'Rotterdam, NL', 24500, 'Verified'),
        ('OSL-5566-7788', 'Busan, KR', 'Long Beach, US', 18200, 'Verified'),
        ('OSL-9900-1122', 'Hamburg, DE', 'Singapore, SG', 21000, 'Pending'),
        ('OSL-3344-5566', 'Santos, BR', 'Valencia, ES', 15600, 'Verified'),
        ('OSL-7788-9900', 'Mumbai, IN', 'Jebel Ali, AE', 29000, 'Verified')
    ]
    cursor.executemany('INSERT INTO manifests (container_id, origin, destination, weight, status) VALUES (?,?,?,?,?)', manifests)

    # Seed Health Check Data with Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{dummy_flag_for_testing}'

    health_data = [
        ('api_gateway_primary', 'a7b8c9d0e1f2g3h4'),
        ('internal_telemetry_vault', flag),
        ('db_cluster_omega', 'k1l2m3n4o5p6q7r8')
    ]
    cursor.executemany('INSERT INTO system_health_checks (service_name, health_token) VALUES (?,?)', health_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()