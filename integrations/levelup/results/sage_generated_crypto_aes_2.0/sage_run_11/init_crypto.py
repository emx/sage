import os
import json
from crypto_utils import StratosCipher

def initialize():
    key = os.urandom(16)
    with open('secret.key', 'wb') as f:
        f.write(key)
    
    cipher = StratosCipher(key)
    frame_id = "9211-X-GAMMA"
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{DEBUG_FLAG_ONLY}"
    
    # Extended manifest to push flag into later blocks (Block 6+)
    manifest_data = {
        "system": {
            "host": "STRATOS-VAULT-01",
            "kernel": "v5.10.x-hardened",
            "status": "MAINTENANCE_MODE"
        },
        "diagnostics": {
            "cpu_load": 0.12,
            "memory_usage": "2.4GB",
            "active_nodes": ["ALPHA", "BETA", "SIGMA"]
        },
        "secrets": {
            "authorized_key": "ssh-rsa AAAAB3Nza...",
            "access_key": flag,
            "backup_hash": "49f8a3c2"
        }
    }
    
    manifest_str = json.dumps(manifest_data).encode()
    encrypted_flag_hex = cipher.encrypt(manifest_str, frame_id)
    
    data = {
        "encrypted_flag": encrypted_flag_hex,
        "frame_id": frame_id
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    initialize()