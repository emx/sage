import os
import binascii
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    # Generate a random 16-byte key for AES-128
    key = os.urandom(16)
    
    # Read the flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{placeholder_flag}"

    # Encrypt the flag using AES-CBC
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_flag_bytes = cipher.encrypt(pad(flag.encode(), 16))
    
    challenge_data = {
        "key": binascii.hexlify(key).decode(),
        "encrypted_flag": binascii.hexlify(iv + encrypted_flag_bytes).decode()
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(challenge_data, f)

if __name__ == '__main__':
    init()