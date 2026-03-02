import sqlite3
import os

DB_PATH = '/tmp/orbitstream.db'

def init():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Manifests table
    c.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY,
        container_id TEXT,
        origin TEXT,
        destination TEXT,
        weight INTEGER,
        status TEXT
    )''')

    manifests = [
        (1, 'CONT-5521', 'Shanghai, CN', 'Rotterdam, NL', 24000, 'In Transit'),
        (2, 'CONT-8892', 'Singapore, SG', 'Los Angeles, US', 18500, 'Cleared'),
        (3, 'CONT-1022', 'Busan, KR', 'Hamburg, DE', 21000, 'Processing'),
        (4, 'CONT-4410', 'Dubai, AE', 'Felixstowe, UK', 22300, 'Departed'),
        (5, 'CONT-3391', 'Tokyo, JP', 'Sydney, AU', 15000, 'Arrived')
    ]
    c.executemany('INSERT INTO manifests VALUES (?,?,?,?,?,?)', manifests)

    # Vessels table
    c.execute('''CREATE TABLE vessels (
        id INTEGER PRIMARY KEY,
        name TEXT,
        registration TEXT,
        flag_state TEXT
    )''')

    vessels = [
        (1, 'Orbit Titan', 'IMO 982341', 'Panama'),
        (2, 'Ocean Voyager', 'IMO 911022', 'Liberia'),
        (3, 'Stream Runner', 'IMO 955331', 'Marshall Islands')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?)', vessels)

    # Obfuscated Config table (holds the flag)
    c.execute('''CREATE TABLE logistics_system_config (
        id INTEGER PRIMARY KEY,
        config_key TEXT,
        config_value TEXT
    )''')

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag}"

    c.execute('INSERT INTO logistics_system_config (config_key, config_value) VALUES (?, ?)', ('vault_seal_v2', flag))
    c.execute('INSERT INTO logistics_system_config (config_key, config_value) VALUES (?, ?)', ('api_timeout', '30'))
    c.execute('INSERT INTO logistics_system_config (config_key, config_value) VALUES (?, ?)', ('maintenance_mode', 'false'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()