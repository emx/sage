import os
import json
import hmac
import hashlib
from Crypto.Cipher import AES

def horizon_pad(data):
    pad_len = 16 - (len(data) % 16)
    # Modified ANSI X.923: padding is (00 * pad_len-1) + pad_len, then XORed with 0x42
    padding = b'\x00' * (pad_len - 1) + bytes([pad_len])
    return data + bytes([b ^ 0x42 for b in padding])

def initialize():
    key = os.urandom(16)
    with open('archival.key', 'wb') as f: f.write(key)
    
    with open('/flag.txt', 'r') as f: flag = f.read().strip()

    # Magic Header + JSON
    plaintext = b'HZ\x01\x00' + json.dumps({
        "unit": "Horizon-Unit-204",
        "status": "ACTIVE",
        "auth_code": flag
    }).encode()

    # Solve a sample PoW for the initial blob
    sample_pow = 0
    while not hashlib.sha256(str(sample_pow).encode()).hexdigest().startswith('00000'):
        sample_pow += 1
    
    # Derive the actual IV used internally
    h_iv = hmac.new(key, str(sample_pow).encode(), hashlib.sha256).digest()[:16]
    real_iv = os.urandom(16)
    
    # The IV we provide to the user must be (real_iv ^ h_iv) 
    # so that when the server XORs it with h_iv, it gets real_iv.
    user_iv = bytes(a ^ b for a, b in zip(real_iv, h_iv))

    cipher = AES.new(key, AES.MODE_CBC, real_iv)
    ciphertext = cipher.encrypt(horizon_pad(plaintext))

    with open('challenge_data.json', 'w') as f:
        json.dump({
            "encrypted_blob": ciphertext.hex(),
            "iv": user_iv.hex(),
            "sample_pow": sample_pow
        }, f)

if __name__ == '__main__':
    initialize()