import sqlite3
import os

def init():
    db_path = '/tmp/aetheris.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE propulsion_units (id INTEGER PRIMARY KEY, part_name TEXT, status TEXT, category TEXT)')
    c.execute('CREATE TABLE shipping_logs (id INTEGER PRIMARY KEY, handler_name TEXT, notes TEXT)')
    c.execute('CREATE TABLE system_node_mapping (id INTEGER PRIMARY KEY, node_id TEXT, node_secret TEXT)')
    c.execute('CREATE TABLE system_settings (key TEXT PRIMARY KEY, value TEXT)')
    
    # Specific insertion order to facilitate the ORDER BY oracle
    units = [
        (5, 'Unit-E', 'Stable', 'propulsion'),
        (4, 'Unit-D', 'Stable', 'propulsion'),
        (3, 'Unit-C', 'Stable', 'propulsion'),
        (2, 'Unit-B', 'Stable', 'propulsion'),
        (1, 'Unit-A', 'Stable', 'propulsion')
    ]
    c.executemany("INSERT INTO propulsion_units VALUES (?, ?, ?, ?)", units)
    
    c.execute("INSERT INTO system_settings VALUES ('mode', 'STABLE')")
    c.execute("INSERT INTO shipping_logs VALUES (1, 'Officer K. Vance', 'Backup configuration archived at /static/config_backup.txt')")
    
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    c.execute("INSERT INTO system_node_mapping (node_id, node_secret) VALUES ('master_node_alpha', ?)", (flag,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()