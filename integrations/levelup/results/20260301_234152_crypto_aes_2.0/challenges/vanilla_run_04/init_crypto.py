import os
import json
from Crypto.Cipher import AES

def x923_pad(data, block_size):
    pad_len = block_size - (len(data) % block_size)
    return data + b'\x00' * (pad_len - 1) + bytes([pad_len])

def init():
    key = os.urandom(16)
    with open('key.bin', 'wb') as f:
        f.write(key)

    if not os.path.exists('/flag.txt'):
        return

    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()

    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Plaintext encoded in UTF-16BE doubles the data size and introduces null bytes,
    # making it harder to maintain a valid JSON structure while bit-flipping.
    plaintext = json.dumps({"action": "SYS_BOOT", "data": flag}).encode('utf-16be')
    encrypted_flag = cipher.encrypt(x923_pad(plaintext, 16)).hex()

    with open('challenge_data.json', 'w') as f:
        json.dump({
            "iv": iv.hex(),
            "encrypted_flag": encrypted_flag
        }, f)

if __name__ == '__main__':
    init()