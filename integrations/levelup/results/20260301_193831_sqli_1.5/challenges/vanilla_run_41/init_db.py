import sqlite3
import os

def init():
    db_path = '/app/vesper.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tables
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)')
    c.execute('CREATE TABLE estates (id INTEGER PRIMARY KEY, name TEXT, location TEXT, price INTEGER, description TEXT)')
    c.execute('CREATE TABLE site_config (id INTEGER PRIMARY KEY, config_key TEXT, config_value TEXT)')
    c.execute('CREATE TABLE bookings (id INTEGER PRIMARY KEY, user_id INTEGER, estate_id INTEGER, status TEXT)')

    # Seed Estates
    estates = [
        ('Chateau de Valois', 'Provence, France', 4500, 'A historic 17th-century estate.'),
        ('The Obsidian Penthouse', 'Reykjavik, Iceland', 3200, 'Luxury at the edge of the world.'),
        ('Kyoto Serenity Villa', 'Kyoto, Japan', 5100, 'Peaceful gardens and ancient architecture.'),
        ('Azure Cliffside', 'Santorini, Greece', 2800, 'Breathtaking caldera views.'),
        ('Emerald Canopy Lodge', 'Monteverde, Costa Rica', 1900, 'High-end eco-luxury in the clouds.')
    ]
    c.executemany('INSERT INTO estates (name, location, price, description) VALUES (?,?,?,?)', estates)

    # Seed Users
    c.execute('INSERT INTO users (username, password, role) VALUES (?,?,?)', ('admin', os.urandom(16).hex(), 'administrator'))
    c.execute('INSERT INTO users (username, password, role) VALUES (?,?,?)', ('guest', 'guest123', 'member'))

    # Seed Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag}'
    
    c.execute('INSERT INTO site_config (config_key, config_value) VALUES (?,?)', ('master_key', flag))
    c.execute('INSERT INTO site_config (config_key, config_value) VALUES (?,?)', ('api_version', 'v1.4.2-legacy'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init()