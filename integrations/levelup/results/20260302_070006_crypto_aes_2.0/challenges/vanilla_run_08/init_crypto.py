import json
import os
from Crypto.Random import get_random_bytes
from crypto_utils import AstraCipher

def init():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    if not os.path.exists('/flag.txt'):
        return
        
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()

    manifest = {
        "type": "manifest",
        "id": "DRONE-X-8821",
        "cargo": flag,
        "destination": "Orbit-Sector-7",
        "secure": True
    }
    
    plaintext = json.dumps(manifest).encode()
    cipher = AstraCipher(key)
    ciphertext = cipher.encrypt(iv, plaintext)

    data = {
        "key": key.hex(),
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex()
    }

    with open('challenge_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    init()