import os
import json
import struct
import binascii
from crypto_utils import StellarCipher, SecurityEngine

def init():
    key = os.urandom(16)
    salt = binascii.hexlify(os.urandom(8)).decode()
    engine = SecurityEngine(salt)
    
    with open('vault.key', 'wb') as f:
        f.write(key)

    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()

    telemetry_data = f"STELLAR-CONFIDENTIAL-DATA:REPORT_ID:42:SECRET:{flag}".encode()
    
    # Generate IV and Ciphertext manually to handle the mask
    iv = os.urandom(16)
    mask = engine.get_iv_mask()
    actual_iv = bytes(a ^ b for a, b in zip(iv, mask))
    
    from Crypto.Cipher import AES
    cipher_obj = AES.new(key, AES.MODE_CBC, actual_iv)
    
    cipher = StellarCipher(key, engine)
    ct = cipher_obj.encrypt(cipher.pad(telemetry_data))

    payload = iv + ct
    checksum = struct.pack(">I", engine.compute_checksum(payload))
    
    data = {
        "blob": (payload + checksum).hex(),
        "salt": salt
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    init()