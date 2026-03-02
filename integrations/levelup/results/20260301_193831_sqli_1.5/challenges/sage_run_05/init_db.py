import sqlite3
import os

def init():
    db_path = '/app/logistics.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tables
    cursor.execute('CREATE TABLE couriers (id INTEGER PRIMARY KEY, name TEXT, region TEXT, status TEXT)')
    cursor.execute('CREATE TABLE warehouse_inventory (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER, warehouse_id TEXT)')
    cursor.execute('CREATE TABLE vql_system_metadata (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')

    # Seed Data
    couriers = [
        (101, 'James Henderson', 'North America', 'Active'),
        (102, 'Elena Rodriguez', 'European Union', 'Active'),
        (103, 'Hiroshi Tanaka', 'Asia-Pacific', 'On Leave'),
        (104, 'Amara Okafor', 'Africa-Middle East', 'Active')
    ]
    cursor.executemany('INSERT INTO couriers VALUES (?,?,?,?)', couriers)

    inventory = [
        (1, 'Thermal Insulated Containers', 450, 'WH-01-NYC'),
        (2, 'Bio-Hazard Transit Cases', 120, 'WH-04-BER'),
        (3, 'Global GPS Trackers (V4)', 3200, 'WH-09-HKG'),
        (4, 'Cryogenic Storage Units', 15, 'WH-01-NYC'),
        (5, 'RFID Pallet Tags', 50000, 'WH-12-SIN')
    ]
    cursor.executemany('INSERT INTO warehouse_inventory VALUES (?,?,?,?)', inventory)

    # Insert Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{test_flag_locally}'
    
    cursor.execute('INSERT INTO vql_system_metadata (config_key, config_value) VALUES (?, ?)', ('internal_system_flag', flag))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init()