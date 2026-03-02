import sqlite3
import os

DB_PATH = '/tmp/verdant_axis.db'

def init():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Table 1: Shipments
    c.execute('''CREATE TABLE shipments (id INTEGER PRIMARY KEY, tracking_id TEXT, origin TEXT, destination TEXT, status TEXT, coordinator TEXT)''')
    shipments = [
        (1, 'VA-99201', 'Zurich, CH', 'Boston, USA', 'In Transit', 'Dr. Aris Thorne'),
        (2, 'VA-88122', 'Singapore, SG', 'London, UK', 'Clearing Customs', 'Marcus Vane'),
        (3, 'VA-77210', 'Berlin, DE', 'Tokyo, JP', 'In Transit', 'Elena Rossi')
    ]
    c.executemany('INSERT INTO shipments VALUES (?,?,?,?,?,?)', shipments)

    # Table 2: Telemetry
    c.execute('''CREATE TABLE telemetry (id INTEGER PRIMARY KEY, shipment_id INTEGER, timestamp TEXT, sensor_type TEXT, value TEXT)''')
    telemetry_data = [
        (1, 1, '2024-10-27 10:00:00', 'temp', '-18.4C'),
        (2, 1, '2024-10-27 10:05:00', 'humidity', '12%'),
        (3, 1, '2024-10-27 10:10:00', 'temp', '-18.2C'),
        (4, 2, '2024-10-27 09:30:00', 'temp', '4.1C'),
        (5, 3, '2024-10-27 11:20:00', 'pressure', '1012hPa')
    ]
    c.executemany('INSERT INTO telemetry VALUES (?,?,?,?,?)', telemetry_data)

    # Table 3: Obfuscated flag table
    c.execute('''CREATE TABLE system_vault (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)''')
    
    # Read flag from /flag.txt (written by Dockerfile)
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{LOCAL_TEST_FLAG}"
        
    c.execute('INSERT INTO system_vault (config_key, config_value) VALUES (?,?)', ('global_integrity_token', flag))
    c.execute('INSERT INTO system_vault (config_key, config_value) VALUES (?,?)', ('api_service_account', 'svc_aegis_prod_01'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()