import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        return

    key = os.urandom(16)
    iv = os.urandom(16)
    
    # Added magic sync-word TLMv2 to payload structure
    payload = b"TLMv2" + json.dumps({
        "cmd": "TELEMETRY_LOG",
        "origin": "NovaStream-LEO-04",
        "flag": flag,
        "status": "INTEGRATED"
    }).encode()
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(payload, 16))
    
    with open('challenge_data.json', 'w') as f:
        json.dump({
            "encrypted_flag": (iv + ciphertext).hex(),
            "key": key.hex()
        }, f)

if __name__ == '__main__':
    init()