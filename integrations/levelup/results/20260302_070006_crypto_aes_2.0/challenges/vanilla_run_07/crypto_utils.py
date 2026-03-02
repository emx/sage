import binascii
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class CelestialCrypto:
    def __init__(self, key):
        self.key = key

    def validate_command(self, iv, ciphertext):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            
            # Step 1: Check Padding
            try:
                unpadded = unpad(decrypted, 16)
            except ValueError:
                return False, "PADDING_ERROR"
            
            # Step 2: Check Signature (CRC32)
            if len(unpadded) < 4:
                return False, "SIGNATURE_ERROR"
            
            content = unpadded[:-4]
            received_crc = unpadded[-4:]
            actual_crc = zlib.crc32(content).to_bytes(4, 'big')
            
            if received_crc != actual_crc:
                return False, "SIGNATURE_ERROR"
            
            return True, None
        except Exception:
            return False, "PADDING_ERROR"