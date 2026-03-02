import os
from Crypto.Cipher import AES

class SatelliteCrypto:
    def __init__(self, key):
        self.key = key
        self.block_size = 16
        self.magic_header = b"AETH"

    def _calc_checksum(self, chunk):
        """Linear checksum using bitwise rotation for positional dependency."""
        chk = 0
        for i, b in enumerate(chunk):
            # Rotate left by i % 8
            rotated = ((b << (i % 8)) | (b >> (8 - (i % 8)))) & 0xFF
            chk ^= rotated
        return chk

    def _pad(self, data):
        # PKCS#7 sequence adjusted for our 15-byte data chunks
        pad_len = 15 - (len(data) % 15)
        padding = bytes([(pad_len ^ 0x42)] * pad_len)
        data += padding
        
        # Break into 15-byte chunks and prepend checksum to each to make 16-byte blocks
        blocks = []
        for i in range(0, len(data), 15):
            chunk = data[i:i+15]
            chk = self._calc_checksum(chunk)
            blocks.append(bytes([chk]) + chunk)
        return b"".join(blocks)

    def _unpad(self, decrypted_data):
        # Extract 15-byte data chunks from 16-byte blocks
        raw_payload = b""
        for i in range(0, len(decrypted_data), 16):
            block = decrypted_data[i:i+16]
            # Checksum is at index 0
            if block[0] != self._calc_checksum(block[1:]):
                raise ValueError("ERR_DSAS_001")
            raw_payload += block[1:]

        last_byte = raw_payload[-1]
        pad_len = last_byte ^ 0x42
        
        if pad_len < 1 or pad_len > 15:
            raise ValueError("ERR_DSAS_002")
        
        for i in range(len(raw_payload) - pad_len, len(raw_payload)):
            if raw_payload[i] ^ 0x42 != pad_len:
                raise ValueError("ERR_DSAS_002")
        
        return raw_payload[:-pad_len]

    def encrypt(self, plaintext):
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Payload must include magic header
        processed_data = self._pad(self.magic_header + plaintext)
        ciphertext = cipher.encrypt(processed_data)
        return ciphertext.hex(), iv.hex()

    def validate_packet(self, ciphertext, iv):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            
            # We only validate the checksum and padding of the provided payload's tail
            # This allows the oracle to function via block truncation.
            try:
                plaintext = self._unpad(decrypted)
            except ValueError as e:
                return False, str(e)

            if not plaintext.startswith(self.magic_header):
                return False, "ERR_DSAS_003"

            return True, None
        except Exception:
            return False, "ERR_DSAS_999"