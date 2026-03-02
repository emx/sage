import os
import zlib
from Crypto.Cipher import AES

class PaddingError(Exception): pass
class IntegrityError(Exception): pass

class AESCipher:
    def __init__(self, key):
        self.key = key

    def _custom_unpad(self, data):
        """Modified PKCS7 unpadding with XOR mask."""
        if not data:
            raise PaddingError()
        pad_val = data[-1]
        # The actual padding length is the byte value XORed with 0x5A
        length = pad_val ^ 0x5A
        if length < 1 or length > 16:
            raise PaddingError()
        # Check all padding bytes
        for i in range(1, length + 1):
            if data[-i] != pad_val:
                raise PaddingError()
        return data[:-length]

    def decrypt(self, ciphertext):
        iv = ciphertext[:16]
        ct = ciphertext[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_raw = cipher.decrypt(ct)
        
        try:
            unpadded = self._custom_unpad(decrypted_raw)
        except Exception:
            raise PaddingError()
        
        if len(unpadded) < 4:
            raise IntegrityError()
            
        data = unpadded[:-4]
        stored_crc = unpadded[-4:]
        if zlib.crc32(data).to_bytes(4, 'big') != stored_crc:
            raise IntegrityError()
            
        return data