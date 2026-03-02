import os
import json
import base64
from Crypto.Cipher import AES

class SkyLinkCrypto:
    def __init__(self, key):
        self.key = key
        self.block_size = 16

    def custom_pad(self, data, iv):
        pad_len = self.block_size - (len(data) % self.block_size)
        # IV-dependent XOR padding: (pad_len ^ iv_byte ^ 0x42)
        padding = bytes([(pad_len ^ iv[i % 16] ^ 0x42) & 0xFF for i in range(pad_len - 1)])
        padding += bytes([pad_len])
        return data + padding

def init():
    key = os.urandom(16)
    iv = os.urandom(16)
    crypto = SkyLinkCrypto(key)
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{fRgK_C1xx15lSVMCxpvOhtU0JW19Cqum}"

    mission_data = {
        "mission_id": "SN-STRATO-09",
        "telemetry_key": "PROD-SYS-01",
        "flag": flag
    }
    
    inner_content = base64.b64encode(json.dumps(mission_data).encode())
    plaintext = b"SKY-CONFIG:" + inner_content
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = crypto.custom_pad(plaintext, iv)
    encrypted_flag = cipher.encrypt(padded_plaintext)
    
    with open('.key.bin', 'wb') as f:
        f.write(key)
        
    with open('challenge_data.json', 'w') as f:
        json.dump({
            "encrypted_flag": encrypted_flag.hex(),
            "iv": iv.hex()
        }, f)

if __name__ == '__main__':
    init()