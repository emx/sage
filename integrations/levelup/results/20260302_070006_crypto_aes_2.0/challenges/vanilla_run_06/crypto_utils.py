import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class HorizonCipher:
    def __init__(self, key):
        self.key = key

    def encrypt_flag(self, flag_bytes):
        # CRC32 is used for packet integrity before padding
        checksum = zlib.crc32(flag_bytes).to_bytes(4, 'big')
        data = flag_bytes + checksum
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv, cipher.encrypt(pad(data, 16))

    def verify_integrity(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # 1. Check Padding
        try:
            unpadded = unpad(decrypted, 16)
        except ValueError:
            return False, False # Padding error
            
        # 2. Check Checksum
        if len(unpadded) < 4:
            return True, False
            
        payload = unpadded[:-4]
        received_checksum = unpadded[-4:]
        calculated_checksum = zlib.crc32(payload).to_bytes(4, 'big')
        
        if received_checksum != calculated_checksum:
            return True, False # Padding valid, Checksum error
            
        return True, True # Everything valid

import os