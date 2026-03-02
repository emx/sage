import sqlite3
import os

def init():
    db_path = '/tmp/vortex_sentry.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE vortex_users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute("INSERT INTO vortex_users (username, password) VALUES ('admin', 'VortexAdmin2024!'), ('dispatcher_mark', 'shipitnow'), ('warehouse_lisa', 'inventory_safe')")
    
    c.execute('CREATE TABLE vortex_manifests (id TEXT PRIMARY KEY, client TEXT, status TEXT, last_update TEXT)')
    c.execute("INSERT INTO vortex_manifests VALUES ('VS-9921-A', 'AeroDynamics Inc', 'In Transit', '2024-05-12 14:20')")
    c.execute("INSERT INTO vortex_manifests VALUES ('VS-1044-B', 'BioSynth Lab', 'Delivered', '2024-05-11 09:15')")
    c.execute("INSERT INTO vortex_manifests VALUES ('VS-3321-C', 'Global Core', 'Delayed', '2024-05-12 16:45')")
    
    c.execute('CREATE TABLE vortex_inventory (id TEXT PRIMARY KEY, item_name TEXT, item_type TEXT, location TEXT)')
    c.execute("INSERT INTO vortex_inventory VALUES ('1', 'Industrial Cooling Unit', 'Secure Vault', 'Warehouse A')")
    c.execute("INSERT INTO vortex_inventory VALUES ('2', 'Lithium-Ion Battery Pack', 'Standard', 'Warehouse B')")
    c.execute("INSERT INTO vortex_inventory VALUES ('3', 'High-Density Server', 'Secure Vault', 'Warehouse A')")
    
    c.execute('CREATE TABLE vortex_system_meta (id INTEGER PRIMARY KEY, meta_key TEXT, meta_value TEXT)')
    
    flag = "LEVELUP{error_reading_flag}"
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        pass
        
    c.execute("INSERT INTO vortex_system_meta (meta_key, meta_value) VALUES ('system_version', '4.2.1'), ('internal_access_flag', ?), ('api_key_primary', 'VS-778899-X')", (flag,))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()