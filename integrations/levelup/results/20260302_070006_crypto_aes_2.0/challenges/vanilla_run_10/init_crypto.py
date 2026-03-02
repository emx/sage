import json
import os
from Crypto.Random import get_random_bytes
from crypto_utils import ValkyrieCipher

def init():
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{m4ty3JQEN9gmBgPuzSZsHVjyiMIsEAXn}"

    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    vc = ValkyrieCipher(key)
    mission_data = f"Valkyrie-Actual:{flag}"
    ciphertext = vc.encrypt(iv, mission_data.encode())

    with open('challenge_data.json', 'w') as f:
        json.dump({
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex(),
            "key": key.hex()
        }, f)

if __name__ == "__main__":
    init()