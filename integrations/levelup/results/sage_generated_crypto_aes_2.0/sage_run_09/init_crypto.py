import os
import json
from crypto_utils import AESCipher

def init():
    key = os.urandom(16)
    cipher_tool = AESCipher(key)
    try:
        with open('/flag.txt', 'r') as f: flag = f.read().strip()
    except: flag = "LEVELUP{DEBUG_FLAG_NOT_FOUND}"
    
    config_data = {
        "mission_id": "Stratus-4",
        "operator": "AetherLink-Alpha",
        "secret_uplink_key": flag,
        "status": "ORBITAL_READY"
    }
    plaintext = b"SYS" + json.dumps(config_data).encode()
    encrypted_config = cipher_tool.encrypt(plaintext)

    data = {"key": key.hex(), "encrypted_config": encrypted_config}
    with open('challenge_data.json', 'w') as f: json.dump(data, f)

if __name__ == "__main__": init()