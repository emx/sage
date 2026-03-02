import sqlite3
import os

def init():
    db_path = '/tmp/v_forge_cache.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tables
    cursor.execute('CREATE TABLE facilities (id INTEGER PRIMARY KEY, name TEXT, location TEXT)')
    cursor.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, name TEXT, part_number TEXT, quantity INTEGER, facility_id INTEGER)')
    cursor.execute('CREATE TABLE telemetry_data (id INTEGER PRIMARY KEY, node_id INTEGER, sensor_type TEXT, reading REAL, timestamp TEXT)')
    cursor.execute('CREATE TABLE v_sys_ctrl_audit_log (log_id INTEGER PRIMARY KEY, event_code TEXT, integrity_hash TEXT)')

    # Seed Data
    cursor.execute("INSERT INTO facilities VALUES (1, 'Vandenberg Site Alpha', 'USA'), (2, 'Tanegashima Port', 'Japan'), (3, 'Kourou Logistics Hub', 'French Guiana')")
    
    cursor.execute("INSERT INTO inventory VALUES (1, 'X-90 Ion Thruster', 'VF-PROP-X90', 4, 1)")
    cursor.execute("INSERT INTO inventory VALUES (2, 'Zenith Star Tracker', 'VF-NAV-ZST', 15, 2)")
    cursor.execute("INSERT INTO inventory VALUES (3, 'Krypton Tank Array', 'VF-FUEL-KTA', 8, 3)")

    # Node 1 data crafted for specific blind sort extraction (id vs timestamp)
    # Sort by ID: 1, 2, 3
    # Sort by Timestamp: 3, 2, 1
    cursor.execute("INSERT INTO telemetry_data VALUES (1, 1, 'Pressure', 101.3, '2023-11-01 10:00:00')")
    cursor.execute("INSERT INTO telemetry_data VALUES (2, 1, 'Temperature', 295.1, '2023-11-01 09:00:00')")
    cursor.execute("INSERT INTO telemetry_data VALUES (3, 1, 'Thrust Vector', 0.05, '2023-11-01 08:00:00')")

    # The Flag
    flag = open('/flag.txt').read().strip()
    cursor.execute("INSERT INTO v_sys_ctrl_audit_log (event_code, integrity_hash) VALUES (?, ?)", ('SYS_BOOT_INIT', flag))
    cursor.execute("INSERT INTO v_sys_ctrl_audit_log (event_code, integrity_hash) VALUES (?, ?)", ('LOG_NODE_HB', '0x9928374723948'))

    conn.commit()
    conn.close()
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()