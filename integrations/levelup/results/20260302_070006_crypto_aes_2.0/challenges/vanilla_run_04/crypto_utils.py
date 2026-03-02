import struct
from Crypto.Cipher import AES

class SecurityEngine:
    def __init__(self, salt_hex):
        self.salt = int(salt_hex, 16)

    def compute_checksum(self, data):
        check = self.salt & 0xFFFFFFFF
        for b in data:
            check = ((check << 7) | (check >> 25)) & 0xFFFFFFFF
            check ^= b
            check = (check + 0xdeadbeef) & 0xFFFFFFFF
        return check

    def get_iv_mask(self):
        state = self.salt
        mask = b""
        for _ in range(4):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            mask += struct.pack(">I", state)
        return mask

class StellarCipher:
    def __init__(self, key, engine):
        self.key = key
        self.engine = engine
        self.header = b"STELLAR-"

    def pad(self, data):
        pad_len = 16 - (len(data) % 16)
        return data + b"\x80" + b"\x00" * (pad_len - 1)

    def unpad(self, data):
        if len(data) == 0 or len(data) % 16 != 0:
            raise ValueError("Invalid block length")
        idx = len(data) - 1
        while idx >= 0 and data[idx] == 0x00:
            idx -= 1
        if idx >= 0 and data[idx] == 0x80:
            return data[:idx]
        raise ValueError("Invalid Padding")

    def verify_v3(self, iv, ciphertext):
        # IV whitening step: the actual IV used for decryption is XORed with a salt-derived mask
        mask = self.engine.get_iv_mask()
        actual_iv = bytes(a ^ b for a, b in zip(iv, mask))
        
        cipher = AES.new(self.key, AES.MODE_CBC, actual_iv)
        try:
            decrypted = cipher.decrypt(ciphertext)
            try:
                pt = self.unpad(decrypted)
            except ValueError:
                return 1 # PADDING_ERR
            
            return 0 if pt.startswith(self.header) else 2 # 2 = SCHEMA_ERR
        except Exception:
            return 1