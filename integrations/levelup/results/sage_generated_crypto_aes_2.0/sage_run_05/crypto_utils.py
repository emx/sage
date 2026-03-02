import hashlib
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class VanguardCipher:
    def __init__(self, key):
        self.key = key

    def decrypt_and_check_padding(self, iv, ct):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ct)
        try:
            return unpad(decrypted, AES.block_size)
        except ValueError:
            return None

class ProofOfWork:
    def __init__(self, difficulty=20):
        self.difficulty = difficulty

    def generate_challenge(self):
        return secrets.token_hex(8)

    def verify(self, challenge, nonce):
        h = hashlib.sha256((challenge + str(nonce)).encode()).hexdigest()
        return h.startswith('00000')