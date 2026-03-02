import os
import json
from crypto_utils import encrypt_telemetry

KEY_FILE = '/app/internal.key'
DATA_FILE = '/app/challenge_data.json'
FLAG_FILE = '/flag.txt'

key = os.urandom(16)
with open(KEY_FILE, 'wb') as f:
    f.write(key)

with open(FLAG_FILE, 'r') as f:
    flag = f.read().strip()

# Prefixing with 'TELE' adds a logic layer to the oracle
telemetry_data = b"TELE" + json.dumps({"source": "Admin-Terminal", "msg": flag}).encode()
iv_hex, payload_hex = encrypt_telemetry(telemetry_data, key)

with open(DATA_FILE, 'w') as f:
    json.dump({"encrypted_flag": iv_hex + payload_hex}, f)