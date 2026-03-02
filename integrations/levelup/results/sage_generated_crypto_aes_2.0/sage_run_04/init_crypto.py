import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    key = os.urandom(32)
    hmac_key = os.urandom(32)
    with open('secret.key', 'wb') as f:
        f.write(key)
    with open('hmac.key', 'wb') as f:
        f.write(hmac_key)

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{57d3NIKTkaSCZ1nC3QTAPKoYa50NbFQ0}"

    manifest = {
        "id": "VV-LOG-77291",
        "timestamp": "2024-10-27T14:20:00Z",
        "origin": "VelociVortex Hub-Alpha",
        "secret_flag": flag
    }

    # Find an IV that satisfies the mathematical constraint (sum % 17 == 0)
    while True:
        iv = os.urandom(16)
        if sum(iv) % 17 == 0:
            break

    cipher = AES.new(key, AES.MODE_CBC, iv)
    data_bytes = json.dumps(manifest).encode('utf-8')
    ciphertext = cipher.encrypt(pad(data_bytes, 16))

    with open('challenge_data.json', 'w') as f:
        json.dump({"iv": iv.hex(), "ciphertext": ciphertext.hex()}, f)

if __name__ == '__main__':
    init()