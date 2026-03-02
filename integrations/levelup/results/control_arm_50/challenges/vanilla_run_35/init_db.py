import sqlite3
import os

def init():
    db = sqlite3.connect('/tmp/veloscore.db')
    cursor = db.cursor()

    # Inventory table
    cursor.execute('''CREATE TABLE inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_name TEXT NOT NULL,
        sku TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )''')

    parts = [
        ('Titanium Actuator X1', 'ACT-9901-TX', 'Actuators', 42),
        ('Precision Servo Motor', 'SRV-2234-P', 'Motors', 156),
        ('Thermal Sensor Array', 'SNS-4402-T', 'Sensors', 89),
        ('High-Load Hydraulic Pump', 'PMP-1102-H', 'Hydraulics', 12),
        ('Carbon Fiber Drive Shaft', 'SFT-7721-C', 'Structural', 67),
        ('Optic Control Module', 'OPT-5561-M', 'Control', 34),
        ('Modular Grid Inverter', 'INV-3320-G', 'Power', 21)
    ]
    cursor.executemany('INSERT INTO inventory (part_name, sku, category, quantity) VALUES (?, ?, ?, ?)', parts)

    # Hidden system table with the flag
    cursor.execute('''CREATE TABLE system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT NOT NULL,
        setting_value TEXT NOT NULL
    )''')

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag}"

    cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('internal_integrity_check', ?)", (flag,))
    cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('api_version', 'v2.4.1-stable')")
    cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('maintenance_mode', 'false')")

    db.commit()
    db.close()

if __name__ == '__main__':
    init()