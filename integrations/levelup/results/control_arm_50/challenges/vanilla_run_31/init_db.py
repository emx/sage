import sqlite3
import os

def init():
    db_path = '/app/production.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'redacted_super_secret_1337', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'renewable2024', 'engineer')")
    
    c.execute('CREATE TABLE nodes (id INTEGER PRIMARY KEY, node_name TEXT, status TEXT)')
    c.execute("INSERT INTO nodes (node_name, status) VALUES ('Solar-Alpha-01', 'active')")
    c.execute("INSERT INTO nodes (node_name, status) VALUES ('Solar-Beta-02', 'active')")
    c.execute("INSERT INTO nodes (node_name, status) VALUES ('Wind-Gamma-05', 'maintenance')")
    
    c.execute('CREATE TABLE system_vault (id INTEGER PRIMARY KEY, vault_key TEXT, vault_value TEXT)')
    
    flag_val = 'LEVELUP{8IC7n4bfHHZiJiIM_IOU7nP6WeXDH5hL}'
    try:
        with open('/flag.txt', 'r') as f:
            flag_val = f.read().strip()
    except:
        pass

    c.execute("INSERT INTO system_vault (vault_key, vault_value) VALUES ('emergency_access_token', ?)", (flag_val,))
    c.execute("INSERT INTO system_vault (vault_key, vault_value) VALUES ('db_encryption_key', '7f8e9a0b1c2d3e4f5a6b7c8d9e0f1a2b')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()