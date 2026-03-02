import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        # Deterministic IV for consistency in challenge generation
        iv = hashlib.sha256(self.key).digest()[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct_bytes = cipher.encrypt(pad(data, 16))
        return iv.hex(), ct_bytes.hex()

    def decrypt_raw(self, ct, iv):
        if len(ct) % 16 != 0:
            return b""
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.decrypt(ct)

def verify_pow(token, nonce, difficulty=5):
    if not nonce: return False
    check = hashlib.sha256((nonce + token).encode()).hexdigest()
    return check.startswith('0' * difficulty)