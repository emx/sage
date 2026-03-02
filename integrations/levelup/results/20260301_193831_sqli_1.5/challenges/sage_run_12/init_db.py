import sqlite3
import os

def init():
    conn = sqlite3.connect('vexillum.db')
    c = conn.cursor()
    
    c.execute('CREATE TABLE shipments (id INTEGER PRIMARY KEY, container_id TEXT, origin TEXT, destination TEXT)')
    c.execute("INSERT INTO shipments VALUES (1, 'VX-7721', 'Rotterdam', 'New York')")
    c.execute("INSERT INTO shipments VALUES (2, 'VX-8890', 'Shanghai', 'Los Angeles')")
    c.execute("INSERT INTO shipments VALUES (3, 'VX-1102', 'Hamburg', 'Singapore')")
    
    c.execute('CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, coords TEXT)')
    c.execute("INSERT INTO vessels VALUES (1, 'Vexillum Star', '51.5074° N, 0.1278° W')")
    c.execute("INSERT INTO vessels VALUES (2, 'Oceanic Voyager', '34.0522° N, 118.2437° W')")
    
    c.execute('CREATE TABLE audit_logs (log_id TEXT PRIMARY KEY, status TEXT)')
    c.execute("INSERT INTO audit_logs VALUES ('101', 'COMPLETED')")
    c.execute("INSERT INTO audit_logs VALUES ('102', 'PENDING')")
    c.execute("INSERT INTO audit_logs VALUES ('103', 'FAILED')")
    
    c.execute('CREATE TABLE app_registry (registry_key TEXT, registry_value TEXT)')
    c.execute("INSERT INTO app_registry VALUES ('system_version', 'v2.4.1-legacy')")
    c.execute("INSERT INTO app_registry VALUES ('environment', 'production')")
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO app_registry VALUES ('flag_token', ?)", (flag,))
    except:
        c.execute("INSERT INTO app_registry VALUES ('flag_token', 'FLAG_NOT_FOUND_IN_BUILD')")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()