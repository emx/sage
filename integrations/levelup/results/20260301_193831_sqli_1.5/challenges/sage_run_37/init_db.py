import sqlite3
import os

def init():
    db_path = '/tmp/aetherflow.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_no TEXT, origin TEXT, destination TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE inventory (id INTEGER PRIMARY KEY, item_name TEXT, quantity INTEGER, warehouse TEXT)''')
    cursor.execute('''CREATE TABLE system_audit (id INTEGER PRIMARY KEY, audit_key TEXT, audit_log TEXT)''')
    
    # Insert seed data
    shipments = [
        ('AF-1001', 'Berlin, DE', 'New York, US', 'In Transit'),
        ('AF-1002', 'Singapore, SG', 'London, UK', 'Processing'),
        ('AF-1003', 'Tokyo, JP', 'Los Angeles, US', 'Delivered'),
        ('AF-1004', 'Dubai, AE', 'Paris, FR', 'Pending'),
        ('AF-1005', 'Shanghai, CN', 'Rotterdam, NL', 'In Transit'),
        ('AF-1006', 'Mumbai, IN', 'Sydney, AU', 'Processing')
    ]
    cursor.executemany("INSERT INTO shipments (tracking_no, origin, destination, status) VALUES (?, ?, ?, ?)", shipments)
    
    inventory = [
        ('Industrial Turbines', 5, 'Warehouse A'),
        ('Medical Supplies', 1200, 'Warehouse B'),
        ('Consumer Electronics', 450, 'Warehouse C'),
        ('Textiles', 800, 'Warehouse A')
    ]
    cursor.executemany("INSERT INTO inventory (item_name, quantity, warehouse) VALUES (?, ?, ?)", inventory)
    
    # Insert Flag into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_audit (audit_key, audit_log) VALUES ('internal_vault_key', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO system_audit (audit_key, audit_log) VALUES ('internal_vault_key', 'LEVELUP{placeholder_flag}')")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()