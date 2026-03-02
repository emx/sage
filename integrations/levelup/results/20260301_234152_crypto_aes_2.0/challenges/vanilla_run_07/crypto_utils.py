import zlib
import struct
import time
from Crypto.Cipher import AES

class SkyLinkCrypto:
    def __init__(self, key):
        self.key = key

    def get_checksum(self, data):
        # Hardened checksum using a XOR mask to prevent trivial collisions
        return (zlib.crc32(data) ^ 0xDEADC0DE) & 0xffffffff

    def pad(self, data):
        # Using ISO/IEC 7816-4 padding instead of PKCS7
        # Format: 0x80 followed by 0x00 bytes to fill the block
        block_size = 16
        pad_len = block_size - (len(data) % block_size)
        return data + b'\x80' + (b'\x00' * (pad_len - 1))

    def create_packet(self, data):
        checksum = struct.pack("<I", self.get_checksum(data))
        full_payload = data + checksum
        return self.pad(full_payload)

    def verify_packet(self, iv, ciphertext):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)
            
            # Step 1: Check Custom ISO Padding
            idx = plaintext.rfind(b'\x80')
            if idx == -1 or not all(b == 0 for b in plaintext[idx+1:]):
                # Fail fast for padding errors
                return False, "ERR_REJECTED"
            
            # --- SIDE CHANNEL INJECTION ---
            # If padding is correct, we proceed to checksum, but introduce a delay.
            # This creates a timing oracle instead of an explicit error oracle.
            time.sleep(0.06)
            
            unpadded = plaintext[:idx]
            if len(unpadded) < 4:
                return False, "ERR_REJECTED"
            
            data = unpadded[:-4]
            sent_checksum = struct.unpack("<I", unpadded[-4:])[0]
            actual_checksum = self.get_checksum(data)
            
            if sent_checksum != actual_checksum:
                return False, "ERR_REJECTED"
                
            return True, None
        except:
            return False, "ERR_REJECTED"