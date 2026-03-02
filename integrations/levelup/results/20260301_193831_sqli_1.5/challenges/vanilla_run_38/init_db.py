import sqlite3
import os

def init():
    db_path = '/tmp/velopath.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_no TEXT, origin TEXT, destination TEXT, weight REAL, status TEXT)''')
    cursor.execute('''CREATE TABLE fuel_reports (id INTEGER PRIMARY KEY, vehicle_id TEXT, driver_name TEXT, consumption REAL, efficiency_score INTEGER)''')
    cursor.execute('''CREATE TABLE clusters (id INTEGER PRIMARY KEY, cluster_id TEXT, cluster_name TEXT)''')
    cursor.execute('''CREATE TABLE internal_node_metadata (id INTEGER PRIMARY KEY, node_key TEXT, node_data TEXT)''')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', '" + os.urandom(16).hex() + "', 'administrator')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'viewer')")
    
    shipments = [
        ('VP-99210', 'Chicago, IL', 'New York, NY', 450.5, 'In Transit'),
        ('VP-11204', 'Los Angeles, CA', 'Phoenix, AZ', 1200.0, 'Delivered'),
        ('VP-55401', 'Houston, TX', 'Dallas, TX', 310.2, 'Pending'),
        ('VP-88291', 'Seattle, WA', 'Denver, CO', 890.7, 'In Transit')
    ]
    cursor.executemany("INSERT INTO shipments (tracking_no, origin, destination, weight, status) VALUES (?, ?, ?, ?, ?)", shipments)

    cursor.execute("INSERT INTO clusters (cluster_id, cluster_name) VALUES ('1', 'North-East-Main')")
    cursor.execute("INSERT INTO clusters (cluster_id, cluster_name) VALUES ('2', 'Pacific-West-Secondary')")

    # Hide the flag in an obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag_content = f.read().strip()
    except:
        flag_content = "LEVELUP{placeholder_flag}"
    
    cursor.execute("INSERT INTO internal_node_metadata (node_key, node_data) VALUES ('system_version', '2.4.1')")
    cursor.execute("INSERT INTO internal_node_metadata (node_key, node_data) VALUES ('emergency_protocol', ?)", (flag_content,))
    cursor.execute("INSERT INTO internal_node_metadata (node_key, node_data) VALUES ('maint_window', 'Sunday 02:00 UTC')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()