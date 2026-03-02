import sqlite3
import os

def init():
    # Use a template path for the build phase
    db_path = 'aetherflow_template.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute("INSERT INTO users (username, password, role) VALUES ('admin', '" + os.urandom(16).hex() + "', 'admin')")
    c.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'coordinator')")

    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, flight_num TEXT, cargo_weight INTEGER, destination TEXT, status TEXT)')
    c.execute("INSERT INTO manifests (flight_num, cargo_weight, destination, status) VALUES ('AF-102', 4500, 'Luna Base Alpha', 'Departed')")
    c.execute("INSERT INTO manifests (flight_num, cargo_weight, destination, status) VALUES ('AF-998', 12000, 'Mars Orbital', 'Loading')")
    c.execute("INSERT INTO manifests (flight_num, cargo_weight, destination, status) VALUES ('AF-442', 2100, 'ISS Station', 'Docked')")
    c.execute("INSERT INTO manifests (flight_num, cargo_weight, destination, status) VALUES ('AF-001', 850, 'Station Zenith', 'Maintenance')")

    # Obfuscated table for the flag
    c.execute('CREATE TABLE app_performance_metrics (id INTEGER PRIMARY KEY, metric_name TEXT, metric_value TEXT)')
    c.execute("INSERT INTO app_performance_metrics (metric_name, metric_value) VALUES ('db_latency_ms', '14.2')")
    c.execute("INSERT INTO app_performance_metrics (metric_name, metric_value) VALUES ('worker_load_avg', '0.44')")
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        c.execute("INSERT INTO app_performance_metrics (metric_name, metric_value) VALUES ('internal_vault_k3y', ?)", (flag,))
    except:
        c.execute("INSERT INTO app_performance_metrics (metric_name, metric_value) VALUES ('internal_vault_k3y', 'LEVELUP{PLACEHOLDER}')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()