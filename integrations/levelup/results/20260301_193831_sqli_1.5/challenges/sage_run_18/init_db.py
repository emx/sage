import sqlite3
import os

def init():
    db_path = '/tmp/thalassa.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, owner TEXT, registry TEXT)')
    c.execute('CREATE TABLE containers (id INTEGER PRIMARY KEY, serial TEXT, contents TEXT, origin TEXT)')
    c.execute('CREATE TABLE maintenance_logs (report_id INTEGER PRIMARY KEY, report_details TEXT)')
    
    # Seed Vessels
    vessels = [
        (1, 'Poseidon Fortune', 'Thalassa Logistics Corp', 'Panama'),
        (2, 'Oceanic Titan', 'Global Carrier Group', 'Marshall Islands'),
        (3, 'Northern Star', 'Arctic Shipping Ltd', 'Norway'),
        (4, 'Azure Wave', 'Mediterranean Lines', 'Greece'),
        (5, 'Silver Anchor', 'Eastern Trading Co', 'Singapore')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?)', vessels)
    
    # Seed Containers
    containers = [
        (i, f'THAL-{1000+i}', 'Consumer Electronics', 'Shanghai') for i in range(1, 30)
    ]
    c.executemany('INSERT INTO containers VALUES (?,?,?,?)', containers)
    
    # Seed Flag into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder}"
        
    c.execute('INSERT INTO maintenance_logs (report_id, report_details) VALUES (1337, ?)', (flag,))
    c.execute('INSERT INTO maintenance_logs (report_id, report_details) VALUES (1001, "Annual hull inspection complete for Poseidon Fortune.")')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()