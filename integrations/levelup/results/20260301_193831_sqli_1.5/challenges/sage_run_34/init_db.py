import sqlite3
import os

def init():
    db_path = '/tmp/verdaroot.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Seed batches
    cursor.execute('''CREATE TABLE seed_batches (
        batch_id INTEGER PRIMARY KEY,
        strain_name TEXT,
        moisture REAL,
        warehouse TEXT
    )''')
    
    batches = [
        (1001, 'Aura-Corn X2', 12.5, 'North-Alpha'),
        (1002, 'Boreal-Wheat Gen3', 10.2, 'North-Alpha'),
        (1003, 'Calyx-Soybean', 11.8, 'South-Beta'),
        (1004, 'Delta-Rice Hybrid', 13.1, 'East-Gamma'),
        (1005, 'Epsilon-Barley', 9.5, 'West-Delta')
    ]
    cursor.executemany('INSERT INTO seed_batches VALUES (?,?,?,?)', batches)

    # Internal configuration (Flag location)
    cursor.execute('''CREATE TABLE internal_node_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT,
        config_value TEXT
    )''')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{MOCK_FLAG_FOR_TESTING}"

    cursor.execute("INSERT INTO internal_node_configs (config_key, config_value) VALUES ('master_sequencing_key', ?)", (flag,))
    cursor.execute("INSERT INTO internal_node_configs (config_key, config_value) VALUES ('api_gateway_timeout', '60')")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()