import os
from Crypto.Cipher import AES

class PaddingError(Exception):
    pass

class AESCipher:
    def __init__(self, key):
        self.key = key

    def _pad(self, data):
        # Custom XOR-masked PKCS7 padding scheme
        # Standard PKCS7 uses byte N repeated N times. 
        # Here we use (N ^ 0x5A) repeated N times.
        pad_len = 16 - (len(data) % 16)
        pad_val = (pad_len ^ 0x5A).to_bytes(1, 'big')
        return data + (pad_val * pad_len)

    def _unpad(self, data):
        if not data:
            raise PaddingError("Empty data")
        
        last_byte = data[-1]
        pad_len = last_byte ^ 0x5A
        
        if pad_len <= 0 or pad_len > 16:
            raise PaddingError("Invalid padding length")
        
        padding = data[-pad_len:]
        if not all(b == last_byte for b in padding):
             raise PaddingError("Invalid padding structure")
             
        return data[:-pad_len]

    def encrypt(self, plaintext):
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(self._pad(plaintext.encode()))
        return (iv + ct).hex()

    def decrypt(self, hex_data):
        data = bytes.fromhex(hex_data)
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(ct))