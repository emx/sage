import os
import json
from crypto_utils import AstraSyncCipher

MAGIC_HEADER = b"ASTRA_V2:"

def init():
    key = os.urandom(16)
    with open("key.bin", "wb") as f:
        f.write(key)

    try:
        with open("/flag.txt", "r") as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{DEBUG_FLAG}"

    manifest = {
        "manifest_id": "VOL-ASTRA-99",
        "flag": flag
    }
    
    payload = MAGIC_HEADER + json.dumps(manifest).encode()
    cipher_suite = AstraSyncCipher(key)
    full_payload = cipher_suite.encrypt(payload).hex()
    
    with open("challenge_data.json", "w") as f:
        json.dump({"manifest": full_payload}, f)

if __name__ == "__main__":
    init()