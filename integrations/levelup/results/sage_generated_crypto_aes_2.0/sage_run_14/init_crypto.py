import os
import json
from Crypto.Cipher import AES
from crypto_utils import custom_pad

def init():
    key = os.urandom(16)
    iv = os.urandom(16)
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{placeholder_flag_for_testing}"

    # Target telemetry format
    telemetry_data = f'{{"origin":"VO-77","payload":"{flag}","status":"archived"}}'
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(custom_pad(telemetry_data.encode(), 16))
    
    # Pre-pend IV to ciphertext
    full_ct = (iv + ct).hex()
    
    data = {
        "key": key.hex(),
        "encrypted_flag": full_ct
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    init()