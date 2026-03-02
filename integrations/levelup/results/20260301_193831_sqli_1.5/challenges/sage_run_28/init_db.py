import sqlite3
import os

def init():
    flag = open('/flag.txt').read().strip()
    db_path = '/tmp/zenith_aura.db'
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Tables
    c.execute('CREATE TABLE satellite_manifests (id INTEGER PRIMARY KEY, satellite_name TEXT, orbit_type TEXT, client_id TEXT)')
    c.execute('CREATE TABLE launch_windows (id INTEGER PRIMARY KEY, window_start TEXT, window_end TEXT, pad_id TEXT)')
    c.execute('CREATE TABLE system_nodes (node_id INTEGER PRIMARY KEY, status TEXT, location TEXT)')
    c.execute('CREATE TABLE site_config (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')
    
    # Seed Data
    manifests = [
        (1, 'Aura-1', 'LEO', '8812'),
        (2, 'Zenith-X', 'GEO', '4410'),
        (3, 'StarLink-ZA', 'LEO', '9901'),
        (4, 'CommSat-4', 'MEO', '1223')
    ]
    c.executemany('INSERT INTO satellite_manifests VALUES (?,?,?,?)', manifests)
    
    windows = [
        (1, '2024-12-01 08:00', '2024-12-01 12:00', 'LC-39A'),
        (2, '2024-12-15 14:00', '2024-12-15 18:00', 'SLC-40')
    ]
    c.executemany('INSERT INTO launch_windows VALUES (?,?,?,?)', windows)
    
    nodes = [
        (1, 'ACTIVE', 'Cape Canaveral'),
        (2, 'ACTIVE', 'Vandenberg'),
        (3, 'INACTIVE', 'Boca Chica')
    ]
    c.executemany('INSERT INTO system_nodes VALUES (?,?,?)', nodes)
    
    # The Flag
    c.execute('INSERT INTO site_config (config_key, config_value) VALUES ("app_version", "2.4.1")')
    c.execute('INSERT INTO site_config (config_key, config_value) VALUES ("vault_access_token", ?)', (flag,))
    c.execute('INSERT INTO site_config (config_key, config_value) VALUES ("maintenance_mode", "false")')

    conn.commit()
    conn.close()
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()