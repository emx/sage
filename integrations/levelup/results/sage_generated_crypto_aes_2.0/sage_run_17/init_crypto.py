import os
import json
from crypto_utils import SatelliteCrypto

def init():
    key = os.urandom(32)
    with open('telemetry.key', 'wb') as f:
        f.write(key)

    with open('/flag.txt', 'r') as f:
        flag = f.read().strip().encode()

    crypto = SatelliteCrypto(key)
    ciphertext, iv = crypto.encrypt(flag)

    with open('challenge_data.json', 'w') as f:
        json.dump({"ciphertext": ciphertext, "iv": iv}, f)

if __name__ == "__main__":
    init()