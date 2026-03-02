from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(data, 16)).hex()

    def decrypt(self, ct_hex, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ct_hex)
        return unpad(decrypted, 16)