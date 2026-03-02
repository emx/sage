import sqlite3
import os

def init():
    db_path = '/app/velosync.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE vehicles (id INTEGER PRIMARY KEY, name TEXT, type TEXT, status TEXT)''')
    c.execute('''CREATE TABLE manifests (id INTEGER PRIMARY KEY, ship_name TEXT, origin TEXT, destination TEXT, status TEXT)''')
    c.execute('''CREATE TABLE site_config (id INTEGER PRIMARY KEY, attr_name TEXT, attr_value TEXT)''')

    # Seed Data
    vehicles = [
        (101, 'Velo-Truck 01', 'Heavy Duty', 'Active'),
        (102, 'Velo-Truck 05', 'Medium Freight', 'Maintenance'),
        (103, 'Velo-Van 12', 'Light Logistics', 'Active'),
        (104, 'Cargo-Master 9', 'Heavy Duty', 'Active'),
        (105, 'Velo-Truck 09', 'Heavy Duty', 'Decommissioned')
    ]
    c.executemany('INSERT INTO vehicles VALUES (?,?,?,?)', vehicles)

    manifests = [
        (1, 'Oceanic Voyager', 'Shanghai', 'Rotterdam', 'In Transit'),
        (2, 'Sea Dragon', 'Singapore', 'Los Angeles', 'Arrived'),
        (3, 'Atlantic Star', 'New York', 'Hamburg', 'In Transit')
    ]
    c.executemany('INSERT INTO manifests VALUES (?,?,?,?,?)', manifests)

    # The Flag Isolation
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{MOCK_FLAG_FOR_TESTING}"

    c.execute('INSERT INTO site_config (attr_name, attr_value) VALUES (?, ?)', ('canary_token', flag))
    c.execute('INSERT INTO site_config (attr_name, attr_value) VALUES (?, ?)', ('api_version', '2.4.1'))
    c.execute('INSERT INTO site_config (attr_name, attr_value) VALUES (?, ?)', ('maintenance_mode', 'false'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()