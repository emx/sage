import os
import json
import hashlib
from Crypto.Cipher import AES

class AetherCipher:
    def __init__(self, key):
        self.key = key

    def _get_mask(self, iv):
        return iv[0] ^ 0x42

    def _pad(self, data, iv):
        mask = self._get_mask(iv)
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len ^ mask] * pad_len)

    def encrypt(self, plaintext):
        iv = AES.get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(self._pad(plaintext.encode(), iv))
        return iv + ct

def main():
    key = os.urandom(32)
    try:
        with open("/flag.txt", "r") as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{cB_uyL4Yyrg0izHkvQSi9nxMl7KRZenT}"

    manifest = {
        "id": "AETHER-771-FLAG",
        "type": "SECURITY_OVERRIDE",
        "content": flag,
        "origin": "Orbital-Res-4"
    }
    
    cipher = AetherCipher(key)
    encrypted_blob = cipher.encrypt(json.dumps(manifest)).hex()
    
    with open("challenge_data.json", "w") as f:
        json.dump({
            "ENCRYPTED_FLAG": encrypted_blob,
            "GLOBAL_KEY": key.hex()
        }, f)

if __name__ == '__main__':
    main()