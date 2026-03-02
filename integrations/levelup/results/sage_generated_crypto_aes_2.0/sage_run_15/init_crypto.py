import os
import json
from transit_layer import SecureTransit

def init():
    key = os.urandom(16)
    with open('key.bin', 'wb') as f:
        f.write(key)

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{tdAb4Y9VHXBMq0fuQubS8HCnxQ4FWHOX}"

    manifest = {
        "manifest_id": "VAL-CORP-99X",
        "payload": flag
    }
    
    transit = SecureTransit(key)
    token = transit.encrypt(json.dumps(manifest).encode())
    
    with open('challenge_data.json', 'w') as f:
        json.dump({"token": token.hex()}, f)

if __name__ == '__main__':
    init()