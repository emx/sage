import sqlite3
import os

def init():
    db_path = "grain_sentinel.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('CREATE TABLE staff_members (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute('CREATE TABLE silos (id INTEGER PRIMARY KEY, location TEXT, crop_type TEXT, capacity INTEGER)')
    c.execute('CREATE TABLE system_audit_logs (id INTEGER PRIMARY KEY, log_key TEXT, log_value TEXT)')

    # Seed Data
    c.execute("INSERT INTO staff_members (username, password, role) VALUES ('admin', 'P4ssw0rd_VP_2024!', 'Administrator')")
    c.execute("INSERT INTO staff_members (username, password, role) VALUES ('manager_north', 'GrainSafe77', 'Manager')")

    c.execute("INSERT INTO silos (location, crop_type, capacity) VALUES ('Silo-A1', 'Hard Red Spring Wheat', 85)")
    c.execute("INSERT INTO silos (location, crop_type, capacity) VALUES ('Silo-A2', 'Yellow Dent Corn', 42)")
    c.execute("INSERT INTO silos (location, crop_type, capacity) VALUES ('Silo-B1', 'Golden Soybeans', 91)")
    c.execute("INSERT INTO silos (location, crop_type, capacity) VALUES ('Silo-C5', 'Malting Barley', 12)")

    # Flag insertion into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag}"

    c.execute("INSERT INTO system_audit_logs (log_key, log_value) VALUES ('master_telemetry_key', ?)", (flag,))
    c.execute("INSERT INTO system_audit_logs (log_key, log_value) VALUES ('firmware_version', 'v4.0.12-pulse')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()