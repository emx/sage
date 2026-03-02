import os
import json
import random
from Crypto.Cipher import AES
from crypto_utils import SkyLinkCrypto

def init():
    # Generate a secure random master key
    key = os.urandom(16)
    with open('vault.key', 'wb') as f:
        f.write(key)

    if os.path.exists('/flag.txt'):
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    else:
        flag = "LEVELUP{PLACEHOLDER_FLAG}"

    crypto = SkyLinkCrypto(key)
    
    # Add a random prefix and structural noise to the data
    noise = os.urandom(random.randint(8, 16)).hex()
    telemetry_data = json.dumps({
        "sys_id": f"SL-{noise}",
        "auth_level": 4,
        "content": {
            "target": "Stratosphere-9",
            "flag": flag
        }
    }).encode()

    iv = os.urandom(16)
    padded_payload = crypto.create_packet(telemetry_data)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_flag = cipher.encrypt(padded_payload)

    with open('challenge_data.json', 'w') as f:
        json.dump({
            "encrypted_flag": encrypted_flag.hex(),
            "iv": iv.hex()
        }, f)

if __name__ == '__main__':
    init()