import os
import json
import zlib
from Crypto.Cipher import AES
from crypto_utils import ManifestCipher

def init():
    key = os.urandom(32)
    iv = os.urandom(16)
    mc = ManifestCipher(key)

    with open("/flag.txt", "r") as f: 
        flag = f.read().strip()

    manifest_data = {
        "user": "admin_dispatch_alpha",
        "role": "dispatcher",
        "manifest_id": "NS-99210-X",
        "priority": "CRITICAL",
        "secret_code": flag
    }
    
    manifest_json = json.dumps(manifest_data).encode('utf-8')
    crc = (zlib.crc32(manifest_json) & 0xffffffff).to_bytes(4, 'big')
    payload = manifest_json + crc
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_manifest = cipher.encrypt(mc.custom_pad(payload))

    config = {
        "key_hex": key.hex(),
        "iv_hex": iv.hex(),
        "encrypted_manifest_hex": encrypted_manifest.hex()
    }

    with open("challenge_data.json", "w") as f:
        json.dump(config, f)

if __name__ == "__main__":
    init()