import sqlite3
import os

def init():
    db_path = '/tmp/verdant_pulse.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Harvest Logs
    c.execute('CREATE TABLE harvest_logs (id INTEGER PRIMARY KEY, batch_id TEXT, crop_type TEXT, yield_amount REAL, grade TEXT)')
    harvest_data = [
        ('BTCH-001', 'Butterhead Lettuce', 450.5, 'A'),
        ('BTCH-002', 'Sweet Basil', 120.2, 'A+'),
        ('BTCH-003', 'Cherry Tomatoes', 890.0, 'B'),
        ('BTCH-004', 'Baby Spinach', 310.8, 'A')
    ]
    c.executemany('INSERT INTO harvest_logs (batch_id, crop_type, yield_amount, grade) VALUES (?,?,?,?)', harvest_data)

    # Nutrient Profiles
    c.execute('CREATE TABLE nutrient_profiles (id INTEGER PRIMARY KEY, profile_name TEXT, nitrogen INTEGER, phosphorus INTEGER, potassium INTEGER)')
    nutrient_data = [
        ('Leafy_Green_V4', 15, 5, 20),
        ('Fruiting_Phase_A', 10, 30, 20),
        ('Seedling_Starter', 20, 20, 20)
    ]
    c.executemany('INSERT INTO nutrient_profiles (profile_name, nitrogen, phosphorus, potassium) VALUES (?,?,?,?)', nutrient_data)

    # Sensor Telemetry
    c.execute('CREATE TABLE sensor_telemetry (id INTEGER PRIMARY KEY, sensor_id TEXT, reading_type TEXT, value REAL, timestamp TEXT)')
    telemetry_data = [
        ('SENS-001', 'Temperature', 22.5, '2024-05-01 10:00:00'),
        ('SENS-002', 'Humidity', 65.2, '2024-05-01 10:00:00'),
        ('SENS-003', 'pH_Level', 6.4, '2024-05-01 10:00:00')
    ]
    c.executemany('INSERT INTO sensor_telemetry (sensor_id, reading_type, value, timestamp) VALUES (?,?,?,?)', telemetry_data)

    # Obfuscated Table for Flag
    c.execute('CREATE TABLE system_node_configs (node_id INTEGER PRIMARY KEY, node_name TEXT, node_secret TEXT, last_sync TEXT)')
    
    flag = "LEVELUP{ERROR_FLAG_NOT_FOUND}"
    if os.path.exists('/flag.txt'):
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
            
    c.execute('INSERT INTO system_node_configs (node_name, node_secret, last_sync) VALUES (?,?,?)', ('Master_Gateway_01', flag, '2024-05-01 08:30:00'))
    
    conn.commit()
    conn.close()
    print("Database initialized at /tmp/verdant_pulse.db")

if __name__ == '__main__':
    init()