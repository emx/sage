import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def calculate_checksum(data_bytes):
    res = 0xDEADBEEF
    for b in data_bytes:
        res = ((res << 7) | (res >> 25)) & 0xFFFFFFFF
        res ^= b
        res = (res * 0x1000193) & 0xFFFFFFFF
    return res

def setup():
    key = os.urandom(16)
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{gfsZ6LeGiIVG93WiQlPIthZY2A4HxuHB}"

    payload = f"AETHER_CMD:DEPLOY_SATELLITE;SECURE_FLAG:{flag};LOG_UUID:{os.urandom(8).hex()}".encode()
    
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(payload, 16))
    
    full_packet = iv + ciphertext
    checksum = calculate_checksum(full_packet)
    
    with open('challenge_data.json', 'w') as f:
        json.dump({
            "ciphertext": full_packet.hex(),
            "key": key.hex(),
            "integrity_token": checksum
        }, f)

if __name__ == '__main__':
    setup()