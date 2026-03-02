import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
        
        key = os.urandom(16)
        iv = os.urandom(16)
        manifest = f"AetherFlow Orbital - NebulaVault v2.1\nMission Manifest\nAccess Code: {flag}"
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(manifest.encode(), 16))

        with open('secrets.json', 'w') as f:
            json.dump({'key': key.hex()}, f)

        with open('challenge_data.json', 'w') as f:
            json.dump({'iv': iv.hex(), 'ciphertext': ct.hex()}, f)
    except Exception:
        import sys
        sys.exit(1)

if __name__ == '__main__':
    init()