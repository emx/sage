import sqlite3
import os

def init():
    db_path = '/tmp/stratosvane.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Realistic tables
    cursor.execute('''CREATE TABLE inventory (id INTEGER PRIMARY KEY, part_name TEXT, serial_number TEXT, warehouse_id TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, destination TEXT, launch_window TEXT, payload_weight TEXT)''')
    cursor.execute('''CREATE TABLE telemetry (id INTEGER PRIMARY KEY, tag TEXT, sensor_type TEXT, last_ping TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE legacy_system_registry (registry_key TEXT PRIMARY KEY, registry_entry TEXT)''')

    # Seed inventory
    cursor.executemany("INSERT INTO inventory (part_name, serial_number, warehouse_id, status) VALUES (?, ?, ?, ?)", [
        ('Hall-Effect Thruster X1', 'SN-2900-A', 'WH-KSC-01', 'Available'),
        ('Star Tracker 4000', 'SN-ST-441', 'WH-VAFB-04', 'Available'),
        ('Telemetry Transponder', 'SN-TX-99', 'WH-KSC-01', 'Reserved'),
        ('Li-Ion Battery Array', 'SN-BAT-05', 'WH-KSC-02', 'Available')
    ])

    # Seed shipments
    cursor.executemany("INSERT INTO shipments (destination, launch_window, payload_weight) VALUES (?, ?, ?)", [
        ('GEO-1 (Geostationary)', '2024-Q3', 'Class-A (Heavy)'),
        ('LEO-600 (Low Earth)', '2024-10-12', 'Class-C (Small)'),
        ('MEO-12 (Mid Earth)', '2025-Q1', 'Class-B (Medium)')
    ])

    # Seed telemetry
    cursor.executemany("INSERT INTO telemetry (tag, sensor_type, last_ping, status) VALUES (?, ?, ?, ?)", [
        ('sensor_v1', 'Thermal', '2024-05-20 14:00', 'active'),
        ('propulsion_a', 'Pressure', '2024-05-20 14:05', 'active'),
        ('grid_status', 'Voltage', '2024-05-20 13:55', 'inactive')
    ])

    # Load and insert the flag into the registry
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO legacy_system_registry (registry_key, registry_entry) VALUES (?, ?)", 
                       ('master_control_key', flag))
        cursor.execute("INSERT INTO legacy_system_registry (registry_key, registry_entry) VALUES (?, ?)", 
                       ('system_version', '1.0.4-legacy'))
    except Exception as e:
        print(f"Error loading flag: {e}")

    conn.commit()
    conn.close()
    print("Database initialized at /tmp/stratosvane.db")

if __name__ == '__main__':
    init()