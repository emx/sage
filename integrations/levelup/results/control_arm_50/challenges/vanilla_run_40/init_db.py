import sqlite3

def init():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    # Main Tables
    c.execute('CREATE TABLE inventory_items (id INTEGER PRIMARY KEY, serial TEXT, name TEXT, category TEXT, condition TEXT)')
    c.execute('CREATE TABLE warehouses (id INTEGER PRIMARY KEY, name TEXT, location TEXT, security_level TEXT)')
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, manifest_id TEXT, destination TEXT, priority TEXT, departure_date TEXT)')
    c.execute('CREATE TABLE telemetry_data (id INTEGER PRIMARY KEY, node_id INTEGER, sensor_type TEXT, last_reading TEXT, status TEXT)')
    
    # Obfuscated Flag Table
    c.execute('CREATE TABLE internal_vault (vault_id INTEGER PRIMARY KEY, vault_key TEXT, vault_value TEXT)')

    # Seed Data
    c.execute("INSERT INTO inventory_items (serial, name, category, condition) VALUES ('XJ-901-T', 'Ion Thruster Array', 'Propulsion', 'Certified')")
    c.execute("INSERT INTO inventory_items (serial, name, category, condition) VALUES ('AV-77-B', 'Navigation Computer', 'Avionics', 'New')")
    c.execute("INSERT INTO inventory_items (serial, name, category, condition) VALUES ('LY-P4', 'Lithium-Polymer Cell', 'Power', 'Maintenance Required')")
    
    c.execute("INSERT INTO warehouses (name, location, security_level) VALUES ('Alpha Base', 'Cape Canaveral, FL', 'Class-A')")
    c.execute("INSERT INTO warehouses (name, location, security_level) VALUES ('High-Desert Depot', 'Mojave, CA', 'Class-B')")
    
    c.execute("INSERT INTO manifests (manifest_id, destination, priority, departure_date) VALUES ('STR-2024-001', 'ISS Docking Port 2', 'Critical', '2024-11-15')")
    
    c.execute("INSERT INTO telemetry_data (node_id, sensor_type, last_reading, status) VALUES (1, 'Thermal Couple', '45.2 C', 'NOMINAL')")
    c.execute("INSERT INTO telemetry_data (node_id, sensor_type, last_reading, status) VALUES (1, 'Pressure Gauge', '101.3 kPa', 'NOMINAL')")
    c.execute("INSERT INTO telemetry_data (node_id, sensor_type, last_reading, status) VALUES (1, 'O2 Sensor', '20.9%', 'NOMINAL')")

    # Insert Flag from /flag.txt
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO internal_vault (vault_key, vault_value) VALUES ('master_access_token', ?)", (flag,))
    c.execute("INSERT INTO internal_vault (vault_key, vault_value) VALUES ('system_encryption_iv', '0x99283711002933')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()