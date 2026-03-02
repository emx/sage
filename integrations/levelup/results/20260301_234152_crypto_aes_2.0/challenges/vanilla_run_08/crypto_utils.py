from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

class AES_Manager:
    def __init__(self, key):
        self.key = key

    def decrypt(self, hex_ciphertext):
        try:
            data = binascii.unhexlify(hex_ciphertext)
            if len(data) < 32:
                return False, "Invalid payload length"
            
            iv = data[:16]
            ciphertext = data[16:]
            
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            
            try:
                # This raises ValueError if padding is incorrect, forming the oracle
                unpad(decrypted, 16)
                return True, "Valid manifest structure"
            except ValueError:
                return False, "Invalid structure"
        except Exception:
            return False, "Malformed hex encoding"