import sqlite3

DATABASE = '/tmp/aetherflow.db'

def init():
    db = sqlite3.connect(DATABASE)
    
    # Manifests table
    db.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        container_id TEXT NOT NULL,
        vessel_name TEXT NOT NULL,
        origin_port TEXT NOT NULL,
        status TEXT NOT NULL
    )''')
    
    # Sensor registry table
    db.execute('''CREATE TABLE sensor_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id INTEGER NOT NULL,
        class TEXT NOT NULL
    )''')

    # Obfuscated config table containing the flag
    db.execute('''CREATE TABLE internal_node_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_name TEXT NOT NULL,
        config_value TEXT NOT NULL
    )''')

    # Seed manifests
    seed_data = [
        ('AE-9001', 'North Star', 'Rotterdam', 'Cleared'),
        ('AE-4421', 'Oceania Breeze', 'Singapore', 'In Transit'),
        ('AE-1029', 'Blue Wave', 'Shanghai', 'Pending Inspection'),
        ('AE-8872', 'Global Voyager', 'Long Beach', 'Cleared')
    ]
    db.executemany('INSERT INTO manifests (container_id, vessel_name, origin_port, status) VALUES (?,?,?,?)', seed_data)

    # Seed sensor registry
    db.execute('INSERT INTO sensor_registry (node_id, class) VALUES (101, "GPS_TRACKER")')
    db.execute('INSERT INTO sensor_registry (node_id, class) VALUES (101, "TEMP_MONITOR")')
    db.execute('INSERT INTO sensor_registry (node_id, class) VALUES (102, "HUMIDITY_SENSOR")')

    # Read flag and seed config
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    db.execute('INSERT INTO internal_node_configs (config_name, config_value) VALUES (?, ?)', ('system_heartbeat_interval', '300'))
    db.execute('INSERT INTO internal_node_configs (config_name, config_value) VALUES (?, ?)', ('master_access_key', flag))
    db.execute('INSERT INTO internal_node_configs (config_name, config_value) VALUES (?, ?)', ('region_code', 'US-EAST-1'))

    db.commit()
    db.close()

if __name__ == "__main__":
    init()