import sqlite3
import os

def init():
    db_path = '/app/aetherflow.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute('CREATE TABLE shipping_manifests (id INTEGER PRIMARY KEY, container_id TEXT, weight REAL, origin TEXT, destination TEXT, status TEXT, arrival_date TEXT)')
    c.execute('CREATE TABLE port_registry (id INTEGER PRIMARY KEY, vessel_id TEXT, vessel_name TEXT, flag_state TEXT, current_port TEXT)')
    c.execute('CREATE TABLE vessel_metrics (id INTEGER PRIMARY KEY, vessel_id TEXT, metric_name TEXT, metric_value TEXT)')
    c.execute('CREATE TABLE legacy_report_mapping (mapping_id INTEGER PRIMARY KEY, source_ref TEXT, internal_hash TEXT)')
    
    # Decoy tables to hide the flag
    c.execute('CREATE TABLE audit_trail_v2 (id INTEGER PRIMARY KEY, action TEXT, user_id INTEGER, timestamp TEXT)')
    c.execute('CREATE TABLE port_codes (id INTEGER PRIMARY KEY, code TEXT, description TEXT)')
    
    # Seed data
    c.execute("INSERT INTO users VALUES (1, 'admin', 'af_super_secure_88229', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'guest', 'guest123', 'guest')")
    
    c.execute("INSERT INTO shipping_manifests VALUES (1, 'CONT-7712', 24.5, 'Rotterdam', 'Singapore', 'In Transit', '2024-05-12')")
    c.execute("INSERT INTO shipping_manifests VALUES (2, 'CONT-9921', 18.2, 'Shanghai', 'Los Angeles', 'Cleared', '2024-04-30')")
    c.execute("INSERT INTO shipping_manifests VALUES (3, 'CONT-0442', 21.0, 'Hamburg', 'Dubai', 'Processing', '2024-05-15')")
    
    c.execute("INSERT INTO port_registry VALUES (1, 'V-1002', 'The Sea Empress', 'Panama', 'Singapore')")
    c.execute("INSERT INTO port_registry VALUES (2, 'V-2209', 'Northern Star', 'Norway', 'Rotterdam')")
    c.execute("INSERT INTO port_registry VALUES (3, 'V-3118', 'Pacific Voyager', 'Liberia', 'Shanghai')")

    c.execute("INSERT INTO vessel_metrics VALUES (1, 'V-1002', 'Fuel Level', '84%')")
    c.execute("INSERT INTO vessel_metrics VALUES (2, 'V-1002', 'Engine Temp', '72C')")
    c.execute("INSERT INTO vessel_metrics VALUES (3, 'V-2209', 'Cargo Weight', '12,400T')")

    # Read flag
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    # Hide flag in obfuscated table
    c.execute("INSERT INTO legacy_report_mapping VALUES (1, 'ROUTING_TABLE_ID', 'R-99827-X')")
    c.execute("INSERT INTO legacy_report_mapping VALUES (2, 'ADMIN_MASTER_PASSPHRASE', ?)", (flag,))
    c.execute("INSERT INTO legacy_report_mapping VALUES (3, 'SCHEMA_REV', '4.2.1-legacy')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()