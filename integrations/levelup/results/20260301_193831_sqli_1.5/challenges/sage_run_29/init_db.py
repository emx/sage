import sqlite3
import os

def init():
    conn = sqlite3.connect('terrasync.db')
    c = conn.cursor()
    
    # Tables
    c.execute('CREATE TABLE soil_plots (id INTEGER PRIMARY KEY, region TEXT, crop_type TEXT, status TEXT)')
    c.execute('CREATE TABLE chemistry_metrics (id INTEGER PRIMARY KEY, plot_id INTEGER, ph REAL, nitrogen REAL, phosphorus REAL)')
    c.execute('CREATE TABLE system_logs (id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, user TEXT, event TEXT)')
    c.execute('CREATE TABLE internal_metadata (id INTEGER PRIMARY KEY, config_key TEXT, secret_val TEXT)')

    # Seed data
    plots = [
        (101, 'Midwest-A1', 'Corn', 'Active'),
        (102, 'Delta-B4', 'Cotton', 'Harvested'),
        (103, 'Pacific-C9', 'Almonds', 'Active'),
        (104, 'Valley-D2', 'Wheat', 'Seedling')
    ]
    c.executemany('INSERT INTO soil_plots VALUES (?,?,?,?)', plots)

    logs = [
        ('2024-05-10 08:30:12', 'admin', 'System initialization complete'),
        ('2024-05-10 09:15:44', 'agronomist', 'Fetched soil samples for Plot #101'),
        ('2024-05-10 10:05:01', 'system', 'Backup service started'),
        ('2024-05-10 11:20:33', 'agronomist', 'Updated Plot #103 status to Active'),
        ('2024-05-10 12:00:00', 'admin', 'Master log rotation executed')
    ]
    for log in logs:
        c.execute('INSERT INTO system_logs (timestamp, user, event) VALUES (?,?,?)', log)

    # Flag insertion
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag}'
    
    c.execute('INSERT INTO internal_metadata (config_key, secret_val) VALUES (?, ?)', ('api_master_key', flag))
    c.execute('INSERT INTO internal_metadata (config_key, secret_val) VALUES (?, ?)', ('encryption_iv', '4b39a7c2e1f0'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()