import sqlite3
import os

def init():
    conn = sqlite3.connect('velocis_maritime.db')
    c = conn.cursor()

    # Create tables
    c.execute('CREATE TABLE vessels (id INTEGER PRIMARY KEY, name TEXT, vessel_type TEXT, status TEXT)')
    c.execute('CREATE TABLE cargo_manifests (id TEXT PRIMARY KEY, vessel_id INTEGER, cargo_type TEXT, weight INTEGER, unit TEXT, destination TEXT)')
    c.execute('CREATE TABLE vms_internal_audit (id INTEGER PRIMARY KEY, setting_name TEXT, config_value TEXT)')

    # Seed Vessels
    vessels = [
        (1, 'Evergreen Grace', 'Container Ship', 'In Transit'),
        (2, 'Maersk Horizon', 'Ultra Large Container', 'Docked'),
        (3, 'Atlantic Voyager', 'General Cargo', 'Maintenance'),
        (4, 'Pacific Pioneer', 'Reefer', 'Loading')
    ]
    c.executemany('INSERT INTO vessels VALUES (?,?,?,?)', vessels)

    # Seed Manifests
    manifests = [
        ('C-101', 1, 'Electronics', 4500, 'kg', 'Rotterdam'),
        ('C-102', 1, 'Textiles', 8200, 'kg', 'Rotterdam'),
        ('C-201', 2, 'Automotive Parts', 12000, 'kg', 'Singapore'),
        ('C-305', 3, 'Heavy Machinery', 25000, 'kg', 'New York')
    ]
    c.executemany('INSERT INTO cargo_manifests VALUES (?,?,?,?,?,?)', manifests)

    # Hide the flag in an obfuscated table
    flag = open('/flag.txt').read().strip()
    settings = [
        ('system_version', '4.2.0-legacy'),
        ('api_timeout', '30s'),
        ('system_integrity_hash', flag),
        ('encryption_key_v1', 'redacted_local_only')
    ]
    c.executemany('INSERT INTO vms_internal_audit (setting_name, config_value) VALUES (?,?)', settings)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()