import sqlite3
import os

def init():
    db_path = '/tmp/zenith.db'
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tables
    cursor.execute('CREATE TABLE satellites (id INTEGER PRIMARY KEY, name TEXT, orbit TEXT, status TEXT)')
    cursor.execute('CREATE TABLE telemetry_logs (id INTEGER PRIMARY KEY, satellite_id INTEGER, sensor_type TEXT, value TEXT, timestamp TEXT)')
    cursor.execute('CREATE TABLE app_config_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)')

    # Seed Satellites
    sats = [
        (1, 'Stellar-Link A1', 'LEO - 550km', 'Operational'),
        (2, 'Stellar-Link A2', 'LEO - 548km', 'Operational'),
        (3, 'Stellar-Link B1', 'LEO - 552km', 'Degraded'),
        (4, 'Deep-Space Relay', 'MEO - 20000km', 'Operational')
    ]
    cursor.executemany('INSERT INTO satellites VALUES (?, ?, ?, ?)', sats)

    # Seed Telemetry (Sorted values specifically chosen to make sort differences obvious)
    logs = [
        (1, 1, 'Battery', '98.2%', '2023-10-27 10:00:00'),
        (2, 1, 'Oxygen', '0.0% (N/A)', '2023-10-27 10:05:00'),
        (3, 1, 'Pressure', '0.001 PSI', '2023-10-27 10:10:00'),
        (4, 1, 'Radiation', '12.4 mSv', '2023-10-27 10:15:00'),
        (5, 1, 'Temperature', '-45.2 C', '2023-10-27 10:20:00')
    ]
    cursor.executemany('INSERT INTO telemetry_logs VALUES (?, ?, ?, ?, ?)', logs)

    # Seed Flag into Stealthy Table
    flag_content = "FLAG_NOT_FOUND"
    if os.path.exists('/flag.txt'):
        with open('/flag.txt', 'r') as f:
            flag_content = f.read().strip()
    
    cursor.execute('INSERT INTO app_config_settings (setting_name, setting_value) VALUES (?, ?)', ('internal_api_key', flag_content))
    cursor.execute('INSERT INTO app_config_settings (setting_name, setting_value) VALUES (?, ?)', ('system_node_id', 'ZS-CORE-001'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()