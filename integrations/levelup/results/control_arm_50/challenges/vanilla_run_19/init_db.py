import sqlite3
import os

def init():
    db_path = '/tmp/velopath.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'Thalassa_Super_Secret_99', 'admin')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'coordinator')")

    # Shipments table
    cursor.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_no TEXT, origin TEXT, destination TEXT, cargo_type TEXT, status TEXT)''')
    shipments = [
        ('VP-9821-XA', 'Singapore', 'Rotterdam', 'Electronics', 'In Transit'),
        ('VP-1123-BC', 'Shanghai', 'Los Angeles', 'Medical Supplies', 'Customs Hold'),
        ('VP-4456-ZZ', 'Dubai', 'Hamburg', 'Automotive', 'Delivered'),
        ('VP-0092-KK', 'Tokyo', 'Seattle', 'Industrial', 'At Sea'),
        ('VP-8821-LL', 'Mumbai', 'London', 'Textiles', 'Processing')
    ]
    cursor.executemany("INSERT INTO shipments (tracking_no, origin, destination, cargo_type, status) VALUES (?,?,?,?,?)", shipments)

    # User Reports table
    cursor.execute('''CREATE TABLE user_reports (id INTEGER PRIMARY KEY, user_id INTEGER, report_name TEXT, sort_column TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # System Registry table (Obfuscated flag storage)
    cursor.execute('''CREATE TABLE system_registry (id INTEGER PRIMARY KEY, registry_key TEXT, registry_value TEXT)''')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{LOCAL_TEST_FLAG}"
        
    cursor.execute("INSERT INTO system_registry (registry_key, registry_value) VALUES ('vault_access_token', ?)", (flag,))
    cursor.execute("INSERT INTO system_registry (registry_key, registry_value) VALUES ('last_maintenance_date', '2023-11-15')")
    cursor.execute("INSERT INTO system_registry (registry_key, registry_value) VALUES ('node_id', 'VELO-NODE-04')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()