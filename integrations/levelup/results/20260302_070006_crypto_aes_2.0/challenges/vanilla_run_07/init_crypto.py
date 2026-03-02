import os
import json
import binascii
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    with open('/flag.txt', 'rb') as f:
        flag = f.read().strip()
    
    key = os.urandom(16)
    iv = os.urandom(16)
    
    # Structure: [FLAG] [CRC32(FLAG)]
    signature = zlib.crc32(flag).to_bytes(4, 'big')
    plaintext = flag + signature
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16))
    
    # Prepend IV to the flag for the telemetry endpoint
    full_package = iv + ciphertext
    
    data = {
        "key": key.hex(),
        "encrypted_flag": full_package.hex()
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    init()