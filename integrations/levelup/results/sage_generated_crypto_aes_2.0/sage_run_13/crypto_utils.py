from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class PaddingError(Exception):
    pass

class AetherCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext):
        iv = AES.get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Standard PKCS7 padding
        ct = cipher.encrypt(pad(plaintext.encode(), 16))
        return iv + ct

    def decrypt(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt_padded = cipher.decrypt(ciphertext)
        try:
            return unpad(pt_padded, 16)
        except ValueError:
            raise PaddingError("Invalid padding")