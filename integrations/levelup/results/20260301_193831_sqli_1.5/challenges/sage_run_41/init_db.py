import sqlite3
import os

def init():
    db_path = '/tmp/nebula_avionics.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Realistic tables
    cursor.execute('''
        CREATE TABLE parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            stock_level INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE site_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT NOT NULL,
            config_value TEXT NOT NULL
        )
    ''')

    # Seed inventory
    parts_data = [
        ('Titanium Turbine Blade', 'Engine', 45),
        ('Avionics Logic Board', 'Electronics', 12),
        ('Hydraulic Actuator', 'Landing Gear', 8),
        ('Carbon Fiber Wing Spar', 'Fuselage', 3),
        ('Navigation Sensor Array', 'Electronics', 15),
        ('Fuel Injection Nozzle', 'Engine', 120),
        ('Cabin Pressure Valve', 'Environment', 22)
    ]
    cursor.executemany('INSERT INTO parts (name, category, stock_level) VALUES (?, ?, ?)', parts_data)

    # Insert the flag into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute('INSERT INTO site_config (config_key, config_value) VALUES (?, ?)', ('system_integrity_token', flag))
    except:
        cursor.execute('INSERT INTO site_config (config_key, config_value) VALUES (?, ?)', ('system_integrity_token', 'LEVELUP{placeholder}'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()