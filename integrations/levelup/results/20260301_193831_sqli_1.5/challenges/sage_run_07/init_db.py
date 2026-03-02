import sqlite3
import os

def init():
    db_path = '/tmp/velocita_logistics.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create tables
    c.execute('''CREATE TABLE shipments 
                 (id INTEGER PRIMARY KEY, tracking_id TEXT, origin TEXT, destination TEXT, status TEXT, weight REAL)''')
    
    c.execute('''CREATE TABLE internal_logistics_config 
                 (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')

    # Seed Shipments
    shipments = [
        (1, 'VSD-99210-A', 'Port of Singapore', 'Rotterdam Europort', 'In Transit', 4500.5),
        (2, 'VSD-10293-B', 'Port of Shanghai', 'Los Angeles Terminal', 'Pending', 12000.0),
        (3, 'VSD-44512-C', 'Jebel Ali Port', 'Hamburg Port', 'Arrived', 3200.2),
        (4, 'VSD-88219-D', 'Port of Busan', 'Port of Felixstowe', 'Customs Hold', 890.0),
        (5, 'VSD-33100-E', 'Antwerp Port', 'Port of Santos', 'In Transit', 15600.8),
        (6, 'VSD-77211-F', 'Port Klang', 'Valencia Port', 'Scheduled', 2200.0),
        (7, 'VSD-55412-G', 'Tanjung Pelepas', 'Port of Savannah', 'In Transit', 7100.5),
        (8, 'VSD-22910-H', 'Port of Tokyo', 'Genoa Port', 'Delayed', 540.3),
        (9, 'VSD-11029-I', 'Port of Qingdao', 'Port of Melbourne', 'In Transit', 11000.4),
        (10, 'VSD-66123-J', 'Colombo Port', 'Cape Town Port', 'Arrived', 670.0)
    ]
    c.executemany('INSERT INTO shipments (id, tracking_id, origin, destination, status, weight) VALUES (?,?,?,?,?,?)', shipments)

    # Load flag from isolated file during build
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag}'

    # Insert flag into obfuscated config table
    c.execute('INSERT INTO internal_logistics_config (config_key, config_value) VALUES (?, ?)', 
              ('system_integrity_token', flag))
    c.execute('INSERT INTO internal_logistics_config (config_key, config_value) VALUES (?, ?)', 
              ('maintenance_mode', 'false'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()