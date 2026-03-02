import sqlite3
import os

def init():
    db_path = '/tmp/aetheris.db'
    if os.path.exists(db_path): os.remove(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute("INSERT INTO users VALUES (1, 'guest', 'guest123')")

    c.execute('CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_id TEXT, destination TEXT, status TEXT)')
    c.execute("INSERT INTO shipments VALUES (101, 'ATH-8821', 'Singapore', 'In Transit')")
    c.execute("INSERT INTO shipments VALUES (102, 'ATH-9932', 'Rotterdam', 'Pending')")

    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, shipment_id INTEGER, cargo_type TEXT, weight INTEGER, signature TEXT)')
    # Row 1 and Row 2 have different ID and Weight to show sort changes
    c.execute("INSERT INTO manifests VALUES (10, 101, 'Industrial Pumps', 2500, 'Capt. H. Miller')")
    c.execute("INSERT INTO manifests VALUES (20, 101, 'Precision Electronics', 450, 'Capt. S. Vane')")

    # Obfuscated Flag Table
    c.execute('CREATE TABLE system_internal_state (id INTEGER PRIMARY KEY, state_key TEXT, state_blob TEXT)')
    for i in range(1, 24):
        c.execute(f"INSERT INTO system_internal_state VALUES ({i}, 'audit_checksum_{i}', '0x' || hex(randomblob(4)))")
    
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO system_internal_state VALUES (24, 'maintenance_token', ?)", (flag,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()