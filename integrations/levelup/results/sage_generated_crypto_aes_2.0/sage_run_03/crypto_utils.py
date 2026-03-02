import os
from Crypto.Cipher import AES

class AstraSyncCipher:
    def __init__(self, key):
        self.key = key

    def pad(self, data, block_size=16):
        l = block_size - (len(data) % block_size)
        if l == 0: l = block_size
        pad_char = l ^ 0x42
        return data + bytes([pad_char] * (l - 1)) + bytes([l])

    def unpad(self, padded):
        if not padded or len(padded) % 16 != 0:
            return None
        l = padded[-1]
        if l < 1 or l > 16:
            return None
        pad_char = l ^ 0x42
        if all(b == pad_char for b in padded[-l:-1]):
            return padded[:-l]
        return None

    def encrypt(self, data):
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(self.pad(data))
        return iv + ct

    def decrypt(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        try:
            pt_padded = cipher.decrypt(ciphertext)
            return self.unpad(pt_padded)
        except:
            return None