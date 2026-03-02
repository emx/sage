from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import os

class AetherCipher:
    def __init__(self, key):
        self.key = key
        self.prefix = b"NEBULA:"

    def _get_mask(self, token, iv):
        # Scramble layer is now derived from both token and IV
        # This makes the XOR mask unique for every single block/request
        ctx = hashlib.sha256(token.encode() + iv).digest()
        return ctx[:16]

    def _scramble(self, data, iv, token):
        mask = self._get_mask(token, iv)
        out = bytearray(data)
        for i in range(len(out)):
            out[i] ^= mask[i % 16]
        return bytes(out)

    def encrypt(self, data, iv=None, token="BOOT"):
        if iv is None:
            iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # Add a 1-byte checksum/header byte to distinguish padding vs logic errors
        checksum = sum(data) % 256
        full_data = self.prefix + bytes([checksum]) + data
        
        ct = cipher.encrypt(pad(full_data, 16))
        return self._scramble(ct, iv, token), iv

    def decrypt_and_verify(self, ct, iv, token):
        # 1. Reverse the dynamic scramble
        descrambled_ct = self._scramble(ct, iv, token)
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(descrambled_ct)
        
        # 2. Check Padding (Oracle Stage 1)
        try:
            pt = unpad(decrypted, 16)
        except ValueError:
            return "PADDING_ERR"

        # 3. Check Header and Checksum (Oracle Stage 2)
        if not pt.startswith(self.prefix):
            return "INTEGRITY_ERR"
            
        try:
            provided_checksum = pt[len(self.prefix)]
            actual_data = pt[len(self.prefix)+1:]
            if sum(actual_data) % 256 != provided_checksum:
                return "INTEGRITY_ERR"
        except:
            return "INTEGRITY_ERR"
            
        return "SUCCESS"