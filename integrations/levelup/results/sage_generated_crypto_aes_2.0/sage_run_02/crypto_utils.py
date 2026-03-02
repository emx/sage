from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class SkyLinkCrypto:
    def __init__(self, key):
        self.key = key
        self.block_size = 16

    def encrypt(self, plaintext, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(plaintext, self.block_size))

    def decrypt(self, ciphertext, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        # unpad raises ValueError if padding is incorrect
        return unpad(decrypted, self.block_size)
