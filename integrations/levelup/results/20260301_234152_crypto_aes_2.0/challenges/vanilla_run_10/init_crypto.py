import os
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def main():
    key = os.urandom(16)
    iv_mask = os.urandom(16)
    
    with open('secret.key', 'wb') as f:
        f.write(key)
    with open('mask.bin', 'wb') as f:
        f.write(iv_mask)

    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{2VpvYBf07h7t0Ya9hCwrLb0qF0gyqLEW}"

    plaintext = f"ICARUS_REC:{flag}".encode()
    
    # Encrypt flag with a random base IV
    base_iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, base_iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16))
    
    # The provided_iv ^ iv_mask == base_iv used for decryption
    provided_iv = bytes([a ^ b for a, b in zip(base_iv, iv_mask)])
    
    challenge_data = {
        "encrypted_flag": {
            "iv": provided_iv.hex(),
            "ct": ciphertext.hex()
        }
    }

    with open('challenge_data.json', 'w') as f: 
        json.dump(challenge_data, f)

if __name__ == "__main__":
    main()