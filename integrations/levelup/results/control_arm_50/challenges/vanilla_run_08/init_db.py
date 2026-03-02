import sqlite3
import os

DATABASE = '/tmp/verdant_pulse.db'

def init():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Tables
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, assigned_sector TEXT)')
    cursor.execute('CREATE TABLE soil_records (id INTEGER PRIMARY KEY, sector_name TEXT, site_id TEXT, ph_level REAL, nitrogen INTEGER, recorded_at DATE)')
    cursor.execute('CREATE TABLE maintenance_logs (id INTEGER PRIMARY KEY, asset_tag TEXT, status TEXT, service_date DATE)')
    # Obfuscated table for flag
    cursor.execute('CREATE TABLE system_settings (id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password, assigned_sector) VALUES ('admin', 'p@ssword123', 'North Sector')")
    cursor.execute("INSERT INTO users (username, password, assigned_sector) VALUES ('j.miller', 'verdant2024!', 'Industrial Zone')")

    sectors = ['North Sector', 'North Sector', 'Industrial Zone', 'Valley Plot B']
    for i, s in enumerate(sectors):
        cursor.execute("INSERT INTO soil_records (sector_name, site_id, ph_level, nitrogen, recorded_at) VALUES (?, ?, ?, ?, ?)",
                       (s, f'SITE-{100+i}', 6.2 + (i*0.1), 45 + (i*5), '2023-11-15'))

    cursor.execute("INSERT INTO maintenance_logs (asset_tag, status, service_date) VALUES ('TRAC-990', 'Operational', '2024-01-10')")
    cursor.execute("INSERT INTO maintenance_logs (asset_tag, status, service_date) VALUES ('HARV-122', 'Operational', '2023-12-05')")

    # Insert flag from file
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('internal_api_key', ?)", (flag,))
    except:
        cursor.execute("INSERT INTO system_settings (setting_name, setting_value) VALUES ('internal_api_key', 'ERROR_READING_FLAG')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()