import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

def init():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)

    try:
        with open('/flag.txt', 'rb') as f:
            flag = f.read().strip().decode()

        # Standardized JSON structure for the flag
        plaintext = json.dumps({"telemetry_data": flag}).encode()

        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, 16))

        data = {
            "iv": iv.hex(),
            "payload": ciphertext.hex()
        }
        with open('challenge_data.json', 'w') as f:
            json.dump(data, f)

        with open('secret.key', 'wb') as f:
            f.write(key)
    except Exception as e:
        print(f"Init error: {e}")

if __name__ == '__main__':
    init()