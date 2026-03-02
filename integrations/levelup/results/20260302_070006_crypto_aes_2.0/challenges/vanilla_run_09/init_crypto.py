import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{placeholder_flag}"

    key = os.urandom(32)
    iv = os.urandom(16)
    
    packet_data = {
        "type": "admin_config",
        "description": "Orbital Maneuver Secret Key",
        "telemetry_key": flag
    }
    
    plaintext = json.dumps(packet_data).encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    challenge_data = {
        "key": key.hex(),
        "encrypted_packet": (iv + ciphertext).hex()
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(challenge_data, f)

if __name__ == '__main__':
    init()