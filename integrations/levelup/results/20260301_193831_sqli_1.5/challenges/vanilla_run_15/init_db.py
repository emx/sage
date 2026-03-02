import sqlite3
import os

def init():
    db = sqlite3.connect('astravantage.db')
    cursor = db.cursor()
    
    # Setup tables
    cursor.execute('CREATE TABLE suppliers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, cert_level TEXT)')
    cursor.execute('CREATE TABLE components (id INTEGER PRIMARY KEY, name TEXT, serial TEXT, weight REAL, supplier_id INTEGER)')
    cursor.execute('CREATE TABLE system_vault (id INTEGER PRIMARY KEY, identifier TEXT, vault_token TEXT)')

    # Seed Data
    suppliers = [
        ('Titan Metalworks', 'procurement@titanmetals.com', 'Level 4'),
        ('VacuumDynamics', 'support@vacdynamic.aero', 'Level 5'),
        ('SpacePropulsion Inc', 'sales@spaceprop.io', 'Level 3')
    ]
    cursor.executemany('INSERT INTO suppliers (name, email, cert_level) VALUES (?, ?, ?)', suppliers)

    components = [
        ('Raptor-X Vacuum Nozzle', 'SN-2024-RX-01', 450.5, 3),
        ('LOX Turbopump Assembly', 'SN-TP-992', 120.0, 1),
        ('Cold Gas Thruster Valve', 'VAL-CG-44', 2.3, 2),
        ('Carbon-Fibre Interstage', 'SN-IS-005', 1200.0, 1),
        ('Avionics Control Rack', 'ACR-V4', 45.0, 3)
    ]
    cursor.executemany('INSERT INTO components (name, serial, weight, supplier_id) VALUES (?, ?, ?, ?)', components)

    # The Flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'LEVELUP{placeholder_flag_for_local_testing}'
    
    cursor.execute("INSERT INTO system_vault (identifier, vault_token) VALUES ('MASTER_FLAG', ?)", (flag,))
    
    db.commit()
    db.close()

if __name__ == '__main__':
    init()