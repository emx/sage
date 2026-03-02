import sqlite3
import os

def init():
    db_path = '/app/thalassa_template.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, flag_state TEXT, eta TEXT, berth TEXT)')
    c.execute("INSERT INTO vessels VALUES (1, 'Poseidon Fortune', 'Panama', '2024-10-24 14:00', 'B-12')")
    c.execute("INSERT INTO vessels VALUES (2, 'Aegean Star', 'Greece', '2024-10-25 08:30', 'A-04')")
    
    c.execute('CREATE TABLE containers (id INTEGER PRIMARY KEY, tracking_id TEXT, origin TEXT, destination TEXT, status TEXT)')
    c.execute("INSERT INTO containers VALUES (1, 'TLOG992831', 'Piraeus', 'Alexandria', 'In Transit')")
    c.execute("INSERT INTO containers VALUES (2, 'TLOG441029', 'Limassol', 'Haifa', 'Dispatched')")
    
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, manifest_id TEXT, vessel_id INTEGER, cargo_type TEXT)')
    c.execute("INSERT INTO manifests VALUES (1, 'MAN-9901', 1, 'General Cargo')")
    c.execute("INSERT INTO manifests VALUES (2, 'MAN-2234', 2, 'Hazardous Chemicals')")
    
    # Obfuscated table for the flag
    c.execute('CREATE TABLE system_audit_log (audit_id INTEGER PRIMARY KEY, event_timestamp TEXT, event_type TEXT, audit_payload TEXT)')
    
    # Read flag from /flag.txt
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO system_audit_log (event_timestamp, event_type, audit_payload) VALUES ('2024-01-01 00:00:00', 'system_init', ?)", (flag,))
    c.execute("INSERT INTO system_audit_log (event_timestamp, event_type, audit_payload) VALUES ('2024-01-01 00:05:00', 'user_login', 'Admin session started')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()