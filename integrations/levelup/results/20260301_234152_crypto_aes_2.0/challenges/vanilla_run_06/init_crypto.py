import os
import json
import struct
from crypto_utils import orion_pad, get_crc32, nibble_swap
from Crypto.Cipher import AES

def init():
    try:
        with open('/flag.txt', 'rb') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = b"LEVELUP{DEBUG_FLAG}"

    key = os.urandom(16)
    iv = os.urandom(16)
    header = b"NOLD-ORION-CONF:"
    payload = header + flag
    
    # Integrity check on nibble-swapped payload
    checksum = struct.pack("<I", get_crc32(nibble_swap(payload)))
    full_data = payload + checksum
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Dynamic padding requires the IV
    ct = cipher.encrypt(orion_pad(full_data, iv, 16))
    
    with open('/app/challenge_data.json', 'w') as f:
        json.dump({
            "key": key.hex(),
            "config_iv_ct": (iv + ct).hex()
        }, f)

if __name__ == '__main__':
    init()