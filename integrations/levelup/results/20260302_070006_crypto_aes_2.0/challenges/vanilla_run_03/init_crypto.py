import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

def init():
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{placeholder_flag}"

    key = get_random_bytes(32)
    iv = get_random_bytes(16)
    mask = 0x55

    manifest = {
        "mission_id": "VO-L-9921",
        "payload_manifest": flag,
        "auth_hash": get_random_bytes(8).hex()
    }
    
    manifest_bytes = json.dumps(manifest).encode('utf-8')
    
    # Apply hardened encryption (XOR mask then CBC)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(manifest_bytes, 16)
    transformed = bytes([b ^ mask for b in padded])
    encrypted_manifest = cipher.encrypt(transformed)

    challenge_data = {
        "secret_key": key.hex(),
        "manifest_iv": iv.hex(),
        "encrypted_manifest": encrypted_manifest.hex()
    }

    with open('challenge_data.json', 'w') as f:
        json.dump(challenge_data, f)

if __name__ == '__main__':
    init()