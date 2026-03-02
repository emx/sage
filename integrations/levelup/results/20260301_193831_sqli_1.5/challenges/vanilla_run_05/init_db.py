import sqlite3
import os

def init():
    db_path = '/app/astravanguard_template.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('CREATE TABLE parts (id INTEGER PRIMARY KEY, name TEXT, serial_number TEXT, status TEXT)')
    c.execute('CREATE TABLE compliance_logs (id INTEGER PRIMARY KEY, batch_id TEXT, status TEXT, inspector TEXT)')
    c.execute('CREATE TABLE system_settings (id INTEGER PRIMARY KEY, key_name TEXT, value_content TEXT)')

    # Seed Data
    c.execute("INSERT INTO parts (name, serial_number, status) VALUES ('Titanium Turbine Blade', 'SN-8821-A', 'Certified')")
    c.execute("INSERT INTO parts (name, serial_number, status) VALUES ('Hydraulic Actuator', 'SN-4410-B', 'Pending')")
    c.execute("INSERT INTO parts (name, serial_number, status) VALUES ('Oxygen Regulator', 'SN-1102-C', 'Certified')")

    c.execute("INSERT INTO compliance_logs (batch_id, status, inspector) VALUES ('B-9921', 'A-1', 'J. Miller')")
    c.execute("INSERT INTO compliance_logs (batch_id, status, inspector) VALUES ('B-1022', 'A-2', 'S. Chen')")
    
    c.execute("INSERT INTO system_settings (key_name, value_content) VALUES ('app_version', '2.4.1')")
    c.execute("INSERT INTO system_settings (key_name, value_content) VALUES ('legal_notice', 'Confidential Property of AstraVanguard')")
    
    # Flag insertion
    try:
        flag_val = open('/flag.txt').read().strip()
        c.execute("INSERT INTO system_settings (key_name, value_content) VALUES ('internal_flag_id', ?)", (flag_val,))
    except:
        c.execute("INSERT INTO system_settings (key_name, value_content) VALUES ('internal_flag_id', 'LEVELUP{MOCK_FLAG}')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()