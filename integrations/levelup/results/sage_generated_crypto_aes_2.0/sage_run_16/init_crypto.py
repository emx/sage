import os
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def custom_pad(data, block_size=16):
    pad_len = block_size - (len(data) % block_size)
    padding = bytes([pad_len ^ 0x42] * pad_len)
    return data + padding

def init():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    try:
        with open("/flag.txt", "r") as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{LOCAL_TEST_FLAG}"
        
    manifest = f"CHRONO|VERSION:2.1|TYPE:DISCRETE_FREIGHT|MANIFEST_ID:CL-992182|CONTENTS:{flag}|END"
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(custom_pad(manifest.encode(), 16))
    
    data = {
        "encrypted_dispatch": (iv + ct).hex(),
        "secret_key_hex": key.hex()
    }
    
    with open("challenge_data.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    init()