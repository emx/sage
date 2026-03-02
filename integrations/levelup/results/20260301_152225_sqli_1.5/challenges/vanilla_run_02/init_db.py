import sqlite3
import os

def init():
    db_path = '/tmp/veridian.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Table 1: Vessels
    c.execute('''CREATE TABLE vessels 
                 (id INTEGER PRIMARY KEY, vessel_name TEXT, vessel_type TEXT, region TEXT)''')
    
    vessels = [
        (1, 'Emerald Drifter', 'Harvester', 'North Atlantic'),
        (2, 'Salinity Seeker', 'Telemetry Drone', 'South Pacific'),
        (3, 'Kelp Queen', 'Processor', 'Arctic Circle'),
        (4, 'Deep Blue Horizon', 'Harvester', 'Indian Ocean')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?)', vessels)

    # Table 2: Harvest Batches
    c.execute('''CREATE TABLE harvests 
                 (id INTEGER PRIMARY KEY, vessel_id INTEGER, kelp_type TEXT, 
                  nutrient_salinity REAL, harvest_date TEXT)''')
    
    harvests = [
        (1, 1, 'Giant Kelp', 34.2, '2023-10-01'),
        (2, 1, 'Bull Kelp', 33.8, '2023-10-05'),
        (3, 3, 'Sugar Kelp', 35.1, '2023-09-28'),
        (4, 4, 'Oarweed', 32.9, '2023-10-12'),
        (5, 2, 'Wakame', 34.5, '2023-10-15')
    ]
    c.executemany('INSERT INTO harvests VALUES (?,?,?,?,?)', harvests)

    # Table 3: Obfuscated Secret Table (The Target)
    c.execute('''CREATE TABLE vessel_archive_registry 
                 (id INTEGER PRIMARY KEY, archive_code TEXT, registry_key TEXT)''')
    
    flag = "LEVELUP{UNKNOWN}"
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        pass

    c.execute('INSERT INTO vessel_archive_registry (archive_code, registry_key) VALUES (?, ?)', 
              ('VKM-SEC-ALPHA-9', flag))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()