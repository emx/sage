import os
import json
from crypto_utils import AetherCipher

def init():
    try:
        with open('/flag.txt', 'rb') as f:
            flag = f.read().strip()
    except:
        flag = b"LEVELUP{ffLwrk7vyWZi23dg4WcbNOXwDxaW5R9T}"

    system_key = os.urandom(16)
    with open('system.key', 'wb') as f:
        f.write(system_key)

    cipher = AetherCipher(system_key)
    # Initial flag is encrypted with token "BOOT"
    encrypted_flag, iv = cipher.encrypt(flag, token="BOOT")

    challenge_data = {
        "encrypted_flag": encrypted_flag.hex(),
        "iv": iv.hex(),
        "boot_token": "BOOT"
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(challenge_data, f)

if __name__ == "__main__":
    init()