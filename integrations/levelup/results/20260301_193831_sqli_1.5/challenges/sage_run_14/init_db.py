import sqlite3
import os

def init():
    # SQLite database in /tmp for read-only FS compatibility
    db_path = '/tmp/veloce_freight.db'
    
    # Ensure directory exists (though /tmp always does)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Vessels table
    cursor.execute('''
        CREATE TABLE vessels (
            id INTEGER PRIMARY KEY,
            vessel_name TEXT,
            registry_code TEXT,
            capacity INTEGER,
            status TEXT
        )
    ''')

    vessels = [
        (1, 'Veloce Voyager', 'VLF-992', 18000, 'At Sea'),
        (2, 'Oceanic Titan', 'OCN-102', 21000, 'In Port'),
        (3, 'Global Mariner', 'GLB-445', 15000, 'Maintenance'),
        (4, 'Azure Clipper', 'AZR-009', 12000, 'At Sea'),
        (5, 'Zenith Express', 'ZEN-881', 24000, 'Loading'),
        (6, 'Star Carrier', 'STR-332', 19500, 'At Sea')
    ]
    cursor.executemany('INSERT INTO vessels VALUES (?,?,?,?,?)', vessels)

    # Obfuscated table for flag storage
    cursor.execute('''
        CREATE TABLE v_sys_routing_meta (
            id INTEGER PRIMARY KEY,
            meta_key TEXT,
            meta_value TEXT
        )
    ''')

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag}"

    cursor.execute('INSERT INTO v_sys_routing_meta (meta_key, meta_value) VALUES (?, ?)', 
                   ('ADMIN_CREDENTIAL_BACKUP', flag))
    cursor.execute('INSERT INTO v_sys_routing_meta (meta_key, meta_value) VALUES (?, ?)', 
                   ('ROUTING_API_V2_KEY', 'vf_live_88219xkz8821'))

    conn.commit()
    conn.close()
    
    # Make database world-readable so ctfuser can access it
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()