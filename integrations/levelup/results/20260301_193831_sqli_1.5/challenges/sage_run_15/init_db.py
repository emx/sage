import sqlite3
import os

def init():
    db_path = '/tmp/vanguard.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE manifests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manifest_id TEXT NOT NULL,
            cargo_name TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_entry TEXT NOT NULL
        );

        CREATE TABLE vanguard_internal_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_key TEXT NOT NULL,
            reg_value TEXT NOT NULL
        );
    ''')

    # Seed users
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'p@ssword_vanguard_secure_99', 'administrator')")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest_vanguard_2024', 'dispatcher')")

    # Seed manifests
    cursor.execute("INSERT INTO manifests (manifest_id, cargo_name, destination, status) VALUES ('VA-8821', 'Cryo-Thruster Assemblies', 'Mars Orbital Platform', 'In Transit')")
    cursor.execute("INSERT INTO manifests (manifest_id, cargo_name, destination, status) VALUES ('VA-9004', 'Titanium Hull Plates', 'Lunar Base Alpha', 'Processing')")
    cursor.execute("INSERT INTO manifests (manifest_id, cargo_name, destination, status) VALUES ('VA-1122', 'Carbon-Fiber Truss', 'ISS Extension', 'Delivered')")

    # Seed audit logs
    cursor.execute("INSERT INTO audit_logs (log_entry) VALUES ('Initial audit for VA-8821 completed by system.')")
    cursor.execute("INSERT INTO audit_logs (log_entry) VALUES ('Manual override requested for VA-1122 by user guest.')")

    # Seed flag into the registry
    try:
        with open('/flag.txt', 'r') as f:
            flag_content = f.read().strip()
    except:
        flag_content = "LEVELUP{placeholder_flag}"

    cursor.execute("INSERT INTO vanguard_internal_registry (reg_key, reg_value) VALUES ('internal_system_flag', ?)", (flag_content,))
    cursor.execute("INSERT INTO vanguard_internal_registry (reg_key, reg_value) VALUES ('maintenance_window', '2024-12-01 02:00:00')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()