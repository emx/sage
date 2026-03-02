import os
import json
import binascii
from crypto_utils import aes_encrypt, PKCS7_pad

def init():
    key = os.urandom(16)
    try:
        with open("/flag.txt", "r") as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{ura_2InzsJuFyITwoFCD7mw7cU9EZSBk}"
        
    header = b"VOL-TELEMETRY-V2"
    manifest_data = {
        "origin": "Vanguard-HQ-Earth",
        "cargo_manifest": flag,
        "security_clearance": "O5-VANGUARD"
    }
    
    iv = os.urandom(16)
    # Use the dynamic IV-based padding
    payload = PKCS7_pad(header + json.dumps(manifest_data).encode(), 16, iv)
    ciphertext = aes_encrypt(payload, key, iv)
    
    with open("challenge_data.json", "w") as f:
        json.dump({
            "key": binascii.hexlify(key).decode(),
            "blob": binascii.hexlify(iv + ciphertext).decode()
        }, f)

if __name__ == "__main__":
    init()