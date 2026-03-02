import sqlite3
import os

def init():
    db_path = '/tmp/velostream.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Seed Manifests
    c.execute('CREATE TABLE manifests (id INTEGER PRIMARY KEY, tracking_id TEXT, destination TEXT, status TEXT, timestamp TEXT)')
    manifests = [
        ('VS-99210', 'London, UK', 'In Transit', '2023-10-27 10:00'),
        ('VS-10423', 'Singapore', 'Customs Hold', '2023-10-27 09:30'),
        ('VS-55211', 'Rotterdam, NL', 'Dispatched', '2023-10-27 11:15'),
        ('VS-88392', 'New York, USA', 'Delivered', '2023-10-26 16:45')
    ]
    c.executemany('INSERT INTO manifests (tracking_id, destination, status, timestamp) VALUES (?, ?, ?, ?)', manifests)

    # Seed Drivers
    c.execute('CREATE TABLE drivers (id INTEGER PRIMARY KEY, name TEXT, license_no TEXT, region TEXT)')
    drivers = [
        ('John Miller', 'TX-88219-A', 'North America'),
        ('Svetlana Petrov', 'RU-00293-B', 'Eastern Europe'),
        ('Chen Wei', 'CN-55123-X', 'Asia Pacific'),
        ('Marco Rossi', 'IT-99221-M', 'Southern Europe')
    ]
    c.executemany('INSERT INTO drivers (name, license_no, region) VALUES (?, ?, ?)', drivers)

    # Seed Metrics (Used for Sorting Injection)
    c.execute('CREATE TABLE logistics_metrics (id INTEGER PRIMARY KEY, route_id TEXT, load_weight REAL, fuel_efficiency REAL, arrival_est TEXT)')
    metrics = [
        ('RT-44', 12500.5, 8.2, '4h 20m'),
        ('RT-12', 4200.0, 12.5, '1h 10m'),
        ('RT-89', 28000.2, 5.1, '12h 45m'),
        ('RT-05', 850.0, 15.2, '0h 45m')
    ]
    c.executemany('INSERT INTO logistics_metrics (route_id, load_weight, fuel_efficiency, arrival_est) VALUES (?, ?, ?, ?)', metrics)

    # Seed Maintenance Logs
    c.execute('CREATE TABLE maintenance_logs (id INTEGER PRIMARY KEY, vehicle_id TEXT, date TEXT, technician TEXT, notes TEXT)')
    logs = [
        ('TRK-992', '2023-09-15', 'Sarah Jenkins', 'Brake pad replacement'),
        ('VAN-041', '2023-10-01', 'Mike Ross', 'Oil change and filter')
    ]
    c.executemany('INSERT INTO maintenance_logs (vehicle_id, date, technician, notes) VALUES (?, ?, ?, ?)', logs)

    # Obfuscated Flag Table
    c.execute('CREATE TABLE system_metadata (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')
    
    # Read flag from /flag.txt (only accessible during build)
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{FLAG_NOT_FOUND}'

    configs = [
        ('api_version', '2.4.1'),
        ('environment', 'production'),
        ('auth_master_token', flag),
        ('max_retry_limit', '5')
    ]
    c.executemany('INSERT INTO system_metadata (config_key, config_value) VALUES (?, ?)', configs)

    conn.commit()
    conn.close()
    print("Database initialized successfully at /tmp/velostream.db")

if __name__ == "__main__":
    init()