from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class IcarusCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext):
        iv = AES.get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(plaintext, 16))
        return iv.hex() + ct.hex()

    def decrypt(self, iv, ciphertext):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = cipher.decrypt(ciphertext)
            return unpad(pt, 16)
        except (ValueError, KeyError):
            # Padding error or decryption error
            return None
