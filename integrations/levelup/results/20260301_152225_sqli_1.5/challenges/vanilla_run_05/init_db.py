import sqlite3
import os

def init():
    db_path = '/tmp/auraflow.db'
    if os.path.exists(db_path): os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE media_clips (
        id INTEGER PRIMARY KEY,
        title TEXT,
        category TEXT,
        broadcast_year INTEGER,
        location TEXT,
        director TEXT,
        description TEXT
    )''')
    
    clips = [
        (1, 'The First Moon Walk', 'News', 1969, 'Houston, TX', 'NASA Broadcast', 'Iconic footage of the Apollo 11 mission lunar landing.'),
        (2, 'Berlin Wall Presser', 'Political', 1989, 'Berlin, Germany', 'Gunter Schabowski', 'The moment the borders were announced open.'),
        (3, 'Olympic 100m Sprint', 'Sports', 1988, 'Seoul, Korea', 'NBC Sports', 'The infamous Ben Johnson vs Carl Lewis race.'),
        (4, 'Deep Sea Explorer I', 'Nature', 1975, 'Pacific Ocean', 'Jacques Cousteau', 'First high-quality footage of hydrothermal vents.'),
        (5, 'City Lights Nightlife', 'Stock', 1955, 'New York, NY', 'Anonymous', 'Vintage B-roll of Times Square neon signs.'),
        (6, 'The Beatles Interview', 'Music', 1964, 'London, UK', 'BBC Archive', 'A rare candid interview before the US tour.'),
        (7, 'Winter in the Alps', 'Scenery', 1992, 'Zermatt, Switzerland', 'Hans Meyer', 'Sweeping vistas of the Matterhorn.'),
        (8, 'Microchip Assembly', 'Technology', 1982, 'Silicon Valley, CA', 'Intel Media', 'Historical look at early cleanroom manufacturing.')
    ]
    c.executemany('INSERT INTO media_clips VALUES (?,?,?,?,?,?,?)', clips)
    
    c.execute('''CREATE TABLE app_settings (
        id INTEGER PRIMARY KEY,
        setting_key TEXT UNIQUE,
        setting_value TEXT
    )''')
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{2f8iF2wINbBeFLa7bflimIJ7Le4Yrx6K}'
        
    c.execute('INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?)', ('archive_vault_key', flag))
    c.execute('INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?)', ('api_version', 'v2.4.1-beta'))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()