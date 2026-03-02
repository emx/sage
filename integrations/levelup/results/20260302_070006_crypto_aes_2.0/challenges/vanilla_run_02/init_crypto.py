import os
import json
import zlib
from Crypto.Cipher import AES

def custom_pad(data):
    # Padding length 1-16 to reach 16-byte boundary
    pad_len = 16 - (len(data) % 16)
    # Each pad byte is (pad_len ^ 0x5A)
    return data + bytes([pad_len ^ 0x5A] * pad_len)

def init():
    key = os.urandom(32)
    salt = os.urandom(32).hex()
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    manifest_content = f"AETHERIA-LEO-MANIFEST-V3-PRIMARY-TELEMETRY-KEY:{flag}".encode()
    
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Payload = Data + CRC32 checksum
    payload = manifest_content + zlib.crc32(manifest_content).to_bytes(4, 'big')
    encrypted_manifest = iv + cipher.encrypt(custom_pad(payload))
    
    challenge_data = {
        "manifest": encrypted_manifest.hex(),
        "k": key.hex(),
        "salt": salt
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(challenge_data, f)

if __name__ == '__main__':
    init()