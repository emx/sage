import sqlite3
import os

def init():
    db_path = '/tmp/velolink.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('CREATE TABLE shipments (id INTEGER PRIMARY KEY, manifest_id TEXT, origin TEXT, destination TEXT, status TEXT)')
    c.execute('CREATE TABLE warehouse_nodes (id INTEGER PRIMARY KEY, node_name TEXT, location TEXT)')
    c.execute('CREATE TABLE system_registry (id INTEGER PRIMARY KEY, reg_key TEXT, reg_value TEXT)')

    # Seed Data
    c.execute("INSERT INTO users (username, password) VALUES ('admin', '5up3r_53cur3_v3lo_4dm1n_2024')")
    c.execute("INSERT INTO users (username, password) VALUES ('guest', 'velolink2024')")

    shipments = [
        ('MNF-8821', 'Singapore', 'Los Angeles', 'In Transit'),
        ('MNF-9022', 'Shanghai', 'Rotterdam', 'Processing'),
        ('MNF-1104', 'Hamburg', 'Dubai', 'Delivered'),
        ('MNF-4432', 'Tokyo', 'San Francisco', 'In Transit'),
        ('MNF-5590', 'Mumbai', 'London', 'Customs Hold')
    ]
    c.executemany('INSERT INTO shipments (manifest_id, origin, destination, status) VALUES (?,?,?,?)', shipments)

    nodes = [
        (1, 'Singapore Hub', 'Singapore'),
        (2, 'Rotterdam Center', 'Netherlands'),
        (3, 'NJ Terminal', 'USA')
    ]
    c.executemany('INSERT INTO warehouse_nodes (id, node_name, location) VALUES (?,?,?)', nodes)

    # Read flag and insert into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{dummy_flag_if_file_not_found}'

    c.execute("INSERT INTO system_registry (reg_key, reg_value) VALUES ('maintenance_key', ?)", (flag,))
    c.execute("INSERT INTO system_registry (reg_key, reg_value) VALUES ('api_version', 'v1.4.2-enterprise')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()