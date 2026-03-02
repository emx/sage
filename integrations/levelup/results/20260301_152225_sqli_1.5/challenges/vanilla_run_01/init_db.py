import sqlite3
import os

def init():
    db_path = '/tmp/verdant_axis.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Realistic logistics tables
    c.execute('''CREATE TABLE inventory (
        id INTEGER PRIMARY KEY,
        item_name TEXT,
        weight INTEGER,
        warehouse_id TEXT
    )''')

    c.execute('''CREATE TABLE internal_audit (
        id INTEGER PRIMARY KEY,
        config_key TEXT,
        config_value TEXT
    )''')

    c.execute('''CREATE TABLE warehouses (
        id TEXT PRIMARY KEY,
        location TEXT,
        manager TEXT
    )''')

    # Seed Data
    inventory_data = [
        (101, 'Industrial Turbine Blade', 12500, 'WH-TX-01'),
        (102, 'Medical Centrifuge Unit', 450, 'WH-CA-05'),
        (103, 'Precision Optics Kit', 25, 'WH-NY-02'),
        (104, 'Lithium-Ion Battery Array', 3200, 'WH-TX-01'),
        (105, 'Organic Seed Storage', 500, 'WH-OR-09'),
        (106, 'Aeronautics Control Module', 120, 'WH-CA-05'),
        (107, 'Smart Irrigation Hub', 85, 'WH-OR-09')
    ]
    c.executemany('INSERT INTO inventory VALUES (?,?,?,?)', inventory_data)

    c.execute('INSERT INTO warehouses VALUES ("WH-TX-01", "Houston, TX", "Alice Vance")')
    c.execute('INSERT INTO warehouses VALUES ("WH-CA-05", "San Jose, CA", "Bob Smith")')

    # Insert the flag into the obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag_content = f.read().strip()
        c.execute('INSERT INTO internal_audit (config_key, config_value) VALUES (?, ?)', 
                  ('security_check_hash', flag_content))
        c.execute('INSERT INTO internal_audit (config_key, config_value) VALUES (?, ?)', 
                  ('api_version', '2.4.1-stable'))
    except Exception as e:
        print(f"Error initializing flag: {e}")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()