import sqlite3
import os

def init():
    db_path = '/tmp/aetheris.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Manifest Table
    cursor.execute('''CREATE TABLE manifests (
        id INTEGER PRIMARY KEY,
        cargo_id TEXT,
        weight INTEGER,
        destination TEXT,
        status TEXT
    )''')
    
    manifests = [
        ('AE-109', 1250, 'Low Earth Orbit', 'Scheduled'),
        ('AE-212', 450, 'ISS Docking Node', 'In Transit'),
        ('AE-505', 3000, 'Geostationary Transfer', 'Pending'),
        ('AE-882', 110, 'Lunar Gateway', 'Delayed'),
        ('AE-991', 880, 'Mars Transit Orbit', 'Scheduled')
    ]
    cursor.executemany('INSERT INTO manifests (cargo_id, weight, destination, status) VALUES (?,?,?,?)', manifests)

    # Contractors Table
    cursor.execute('''CREATE TABLE contractors (
        id INTEGER PRIMARY KEY,
        name TEXT,
        clearance_level INTEGER,
        specialization TEXT
    )''')
    
    contractors = [
        ('Elena Vance', 4, 'Orbital Mechanics'),
        ('Marcus Thorne', 3, 'Propulsion Systems'),
        ('Sia Rodriguez', 5, 'Strategic Launch Security'),
        ('Julian Finch', 2, 'Cargo Loading')
    ]
    cursor.executemany('INSERT INTO contractors (name, clearance_level, specialization) VALUES (?,?,?)', contractors)

    # Obfuscated Flag Table
    cursor.execute('''CREATE TABLE log_archive_7712 (
        id INTEGER PRIMARY KEY,
        entry_date TEXT,
        entry_content TEXT
    )''')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag}'

    cursor.execute('INSERT INTO log_archive_7712 (entry_date, entry_content) VALUES (?,?)', ('2023-10-12', f'System Access Key Updated: {flag}'))
    cursor.execute('INSERT INTO log_archive_7712 (entry_date, entry_content) VALUES (?,?)', ('2023-10-11', 'Backup procedure initialized for orbital cluster C-4'))

    conn.commit()
    conn.close()
    
    # Make sure ctfuser can read/write the DB in /tmp
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    init()