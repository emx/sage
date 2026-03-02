from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AstraCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, iv, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(plaintext, 16))

    def decrypt(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # unpad will raise ValueError if padding is invalid
        return unpad(cipher.decrypt(ciphertext), 16)