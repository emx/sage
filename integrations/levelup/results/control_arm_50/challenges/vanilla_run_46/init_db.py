import sqlite3
import os

def init():
    db_path = '/tmp/aetherflow.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Inventory Data
    c.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, sku TEXT, name TEXT, quantity INTEGER, warehouse_id TEXT)')
    skus = [
        ('AF-SKU-001', 'Heavy Lift Propeller', 45, 'SIN-04'),
        ('AF-SKU-092', 'Lithium Polymer Battery 12Ah', 120, 'SIN-04'),
        ('AF-SKU-115', 'GPS Navigation Module v4', 30, 'HKG-02'),
        ('AF-SKU-442', 'Drone Chassis Frame C1', 15, 'SIN-04')
    ]
    c.executemany('INSERT INTO inventory (sku, name, quantity, warehouse_id) VALUES (?,?,?,?)', skus)

    # Drone Status
    c.execute('CREATE TABLE drones (id INTEGER PRIMARY KEY, drone_id TEXT, model TEXT, status TEXT, last_service TEXT)')
    drones = [
        ('DRN-001', 'AetherCarrier X1', 'Active', '2023-10-12'),
        ('DRN-002', 'AetherCarrier X1', 'Maintenance', '2023-11-05'),
        ('DRN-045', 'SwiftScout v2', 'Active', '2023-12-01')
    ]
    c.executemany('INSERT INTO drones (drone_id, model, status, last_service) VALUES (?,?,?,?)', drones)

    # Telemetry (The target for ORDER BY injection)
    c.execute('CREATE TABLE drone_telemetry (id INTEGER PRIMARY KEY, drone_id TEXT, status TEXT, battery_level INTEGER, last_ping TEXT)')
    telemetry = [
        ('DRN-001', 'In-Flight', 88, '14:20:01'),
        ('DRN-045', 'Idle', 100, '14:21:55'),
        ('DRN-102', 'Charging', 22, '14:18:30')
    ]
    c.executemany('INSERT INTO drone_telemetry (drone_id, status, battery_level, last_ping) VALUES (?,?,?,?)', telemetry)

    # Obfuscated Flag Table
    c.execute('CREATE TABLE system_configs (id INTEGER PRIMARY KEY, config_name TEXT, config_value TEXT)')
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    c.execute('INSERT INTO system_configs (config_name, config_value) VALUES (?,?)', ('master_vault_key', flag))
    c.execute('INSERT INTO system_configs (config_name, config_value) VALUES (?,?)', ('api_endpoint_v3', 'https://api-internal.aetherflow.io/v3'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()