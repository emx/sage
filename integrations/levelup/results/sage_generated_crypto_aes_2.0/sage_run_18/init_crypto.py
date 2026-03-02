import os
import json
from Crypto.Cipher import AES
from crypto_utils import DSASManager

def custom_pad(data):
    pad_len = 16 - (len(data) % 16)
    # Matches the position-dependent padding: pad_len ^ index_from_end
    # index_from_end is 1-indexed
    padding = bytes([pad_len ^ i for i in range(pad_len, 0, -1)])
    return data + padding

def initialize():
    with open("/flag.txt", "rb") as f:
        flag = f.read().strip()

    key = os.urandom(32)
    real_iv = os.urandom(16)
    
    manifest = b"VA-MV7|" + flag
    padded_manifest = custom_pad(manifest)

    cipher = AES.new(key, AES.MODE_CBC, real_iv)
    ciphertext = cipher.encrypt(padded_manifest)

    # Reverse the rotation for the provided IV
    # Circular shift right by 1 per byte
    provided_iv = bytes([((b >> 1) | (b << 7)) & 0xFF for b in real_iv])

    with open("challenge_data.json", "w") as f:
        json.dump({
            "iv": provided_iv.hex(),
            "encrypted_manifest": ciphertext.hex()
        }, f)

    with open("vault.key", "wb") as f:
        f.write(key)

if __name__ == "__main__":
    initialize()