from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AetherCipher:
    def __init__(self, key):
        self.key = key
        self.bs = 16

    def encrypt(self, iv, data):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(data, self.bs))

    def decrypt(self, iv, ct):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # This will raise ValueError on bad padding, which the app uses for the oracle
        return unpad(cipher.decrypt(ct), self.bs)
