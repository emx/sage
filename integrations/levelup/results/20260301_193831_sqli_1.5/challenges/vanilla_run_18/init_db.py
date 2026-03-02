import sqlite3
import os

def init():
    db_path = '/tmp/verdant_analytics.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Realistic data tables
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    cursor.execute('''CREATE TABLE harvest_records (id INTEGER PRIMARY KEY, crop_type TEXT, yield_tons REAL, region TEXT, moisture_pct REAL)''')
    cursor.execute('''CREATE TABLE site_settings (setting_id INTEGER PRIMARY KEY, setting_name TEXT, setting_value TEXT)''')

    # Seed Data
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'RedactedPassword2024!'), ('guest', 'guest123')")
    
    crops = [
        ('Corn', 180.5, 'Midwest', 15.2),
        ('Soybeans', 55.2, 'Midwest', 13.0),
        ('Wheat', 72.1, 'Great Plains', 12.5),
        ('Barley', 65.4, 'Pacific Northwest', 11.8),
        ('Oats', 95.0, 'Northeast', 14.1),
        ('Cotton', 850.2, 'Southeast', 10.5),
        ('Rice', 7500.0, 'Delta', 19.5)
    ]
    cursor.executemany("INSERT INTO harvest_records (crop_type, yield_tons, region, moisture_pct) VALUES (?,?,?,?)", crops)

    # Flag insertion into obfuscated table
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = "LEVELUP{placeholder_flag}"

    cursor.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('theme_color', '#2e7d32')")
    cursor.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('max_upload_size', '10MB')")
    cursor.execute("INSERT INTO site_settings (setting_name, setting_value) VALUES ('internal_api_secret', ?)", (flag,))
    
    conn.commit()
    conn.close()
    
    # Ensure the non-root user can read/write the DB at runtime
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()