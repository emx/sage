import sqlite3
import os

def init():
    db_path = '/app/velo_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('driver_admin', 'Veloce2024'))

    # Cargo table
    cursor.execute('''CREATE TABLE cargo_items (
        id INTEGER PRIMARY KEY, 
        tracking_id TEXT, 
        source_city TEXT, 
        destination TEXT, 
        ship_state TEXT
    )''')
    
    shipments = [
        ('VST-1001', 'New York', 'London', 'In Transit'),
        ('VST-1002', 'Hong Kong', 'Singapore', 'Delayed'),
        ('VST-1003', 'Berlin', 'Paris', 'Arrived'),
        ('VST-1004', 'Tokyo', 'San Francisco', 'Processing'),
        ('VST-1005', 'Dubai', 'Mumbai', 'In Transit')
    ]
    cursor.executemany('INSERT INTO cargo_items (tracking_id, source_city, destination, ship_state) VALUES (?, ?, ?, ?)', shipments)

    # Fleet Logs table (Obfuscated Flag Storage)
    cursor.execute('CREATE TABLE fleet_logs (id INTEGER PRIMARY KEY, record_cat TEXT, report_data TEXT)')
    
    # Read flag from file
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag}'

    cursor.execute('INSERT INTO fleet_logs (record_cat, report_data) VALUES (?, ?)', ('maintenance_schedule', 'Oil change for VeloTruck-42 completed.'))
    cursor.execute('INSERT INTO fleet_logs (record_cat, report_data) VALUES (?, ?)', ('system_seal', flag))
    cursor.execute('INSERT INTO fleet_logs (record_cat, report_data) VALUES (?, ?)', ('driver_incident', 'Minor delay at port 7 due to weather.'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()