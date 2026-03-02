import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

def init():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    
    try:
        with open("/flag.txt", "r") as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{kQKiNFzDQ1pCAvVG1TvChtdPSWoyjpSK}"
    
    # narrative formatting
    plaintext = f"ASTRA9_LOG_V2.5:MISSION_CRITICAL_DATA_ENCRYPTED_CHANNEL:{flag}".encode()
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16))
    
    with open("challenge_data.json", "w") as f:
        json.dump({
            "ciphertext": ciphertext.hex(),
            "iv": iv.hex()
        }, f)
    
    with open("secret.key", "wb") as f:
        f.write(key)

if __name__ == "__main__":
    init()