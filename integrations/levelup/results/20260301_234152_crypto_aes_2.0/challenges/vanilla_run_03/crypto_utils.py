from Crypto.Cipher import AES
import json
import zlib

class ManifestCipher:
    def __init__(self, key):
        self.key = key

    def custom_pad(self, data):
        # ISO/IEC 7816-4 Padding
        padding_len = 16 - (len(data) % 16)
        padding = b'\x80' + b'\x00' * (padding_len - 1)
        return data + padding

    def decrypt_and_unpad(self, iv, ciphertext):
        if len(ciphertext) % 16 != 0:
            raise ValueError("Alignment Error")
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        idx = decrypted.rfind(b'\x80')
        if idx == -1:
            raise ValueError("Padding Error")
        
        suffix = decrypted[idx+1:]
        if any(b != 0 for b in suffix):
            raise ValueError("Padding Error")
            
        return decrypted[:idx]

    def validate_structure(self, unpadded):
        if len(unpadded) < 4:
            raise ArithmeticError("Short Payload")
        
        data = unpadded[:-4]
        stored_crc = unpadded[-4:]
        computed_crc = (zlib.crc32(data) & 0xffffffff).to_bytes(4, 'big')
        
        if stored_crc != computed_crc:
            raise ArithmeticError("Checksum Error")
        
        # Ensure valid UTF-8 and JSON
        decoded = data.decode('utf-8')
        json.loads(decoded)
        return decoded

    def decrypt_and_validate(self, iv, ciphertext):
        unpadded = self.decrypt_and_unpad(iv, ciphertext)
        return self.validate_structure(unpadded)