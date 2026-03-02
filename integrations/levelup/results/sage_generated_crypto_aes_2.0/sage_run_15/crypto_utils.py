import os
from Crypto.Cipher import AES

class DSASCrypto:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Manual PKCS7 padding
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len] * pad_len)
        return iv + cipher.encrypt(padded_data)

    def decrypt(self, token: bytes) -> bytes:
        if len(token) < 32 or len(token) % 16 != 0:
            raise ValueError("ERR_DSAS_001")
            
        iv = token[:16]
        ciphertext = token[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # Strict PKCS7 padding validation
        if not decrypted:
            raise ValueError("ERR_DSAS_001")
            
        padding_len = decrypted[-1]
        if padding_len < 1 or padding_len > 16:
            raise ValueError("ERR_DSAS_001")
        
        for i in range(1, padding_len + 1):
            if decrypted[-i] != padding_len:
                raise ValueError("ERR_DSAS_001")
                
        return decrypted[:-padding_len]