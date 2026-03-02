import sqlite3
import os

def init():
    db_path = '/tmp/verdantpath.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE crop_yields (id INTEGER PRIMARY KEY, region TEXT, crop_type TEXT, yield_weight INTEGER)')
    c.execute('CREATE TABLE soil_profiles (id INTEGER PRIMARY KEY, field_id TEXT, n_level REAL, p_level REAL, k_level REAL)')
    c.execute('CREATE TABLE maintenance_logs (id INTEGER PRIMARY KEY, tractor_id TEXT, service_date TEXT, technician TEXT)')
    c.execute('CREATE TABLE system_meta (id INTEGER PRIMARY KEY, key TEXT, data TEXT)')
    
    # Seed data
    yields = [
        ('North-1', 'Corn', 1200), ('North-2', 'Soy', 980), ('East-5', 'Wheat', 1500),
        ('West-1', 'Corn', 1100), ('South-2', 'Cotton', 850), ('Central-4', 'Soy', 1050)
    ]
    c.executemany('INSERT INTO crop_yields (region, crop_type, yield_weight) VALUES (?,?,?)', yields)
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{sU_ijPvPSf1nmSWfUENeyEtM_fO8P8G9}"
        
    c.execute('INSERT INTO system_meta (key, data) VALUES (?, ?)', ('internal_site_key', flag))
    c.execute('INSERT INTO system_meta (key, data) VALUES (?, ?)', ('api_version', 'v2.0.1-stable'))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()