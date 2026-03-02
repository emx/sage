import os
import json
import hmac
import hashlib
from Crypto.Cipher import AES

def iso10126_pad(data, block_size):
    pad_len = block_size - (len(data) % block_size)
    padding = os.urandom(pad_len - 1) + bytes([pad_len])
    return data + padding

def init():
    key = os.urandom(16)
    with open('telemetry.key', 'wb') as f:
        f.write(key)

    with open('/flag.txt', 'rb') as f:
        flag = f.read().strip()

    iv = os.urandom(16)
    integrity_key = hmac.new(key, iv, hashlib.sha256).digest()
    mac = hmac.new(integrity_key, flag, hashlib.sha256).digest()
    data = flag + mac
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(iso10126_pad(data, 16))
    packet = (iv + ciphertext).hex()
    with open('challenge_data.json', 'w') as f:
        json.dump({"admin_packet": packet}, f)

if __name__ == "__main__":
    init()