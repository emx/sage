from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCipher:
    def __init__(self, key):
        self.key = key
        self.bs = 16

    def encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(plaintext, self.bs))
        return cipher.iv, ct_bytes

    def decrypt(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # unpad() raises ValueError if padding is incorrect
        return unpad(cipher.decrypt(ciphertext), self.bs)
