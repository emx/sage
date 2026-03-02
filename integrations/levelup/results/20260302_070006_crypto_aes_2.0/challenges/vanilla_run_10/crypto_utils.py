import json
import hashlib
import hmac
from Crypto.Cipher import AES

class ValkyrieCipher:
    def __init__(self, key):
        self.key = key

    def derive_internal_token(self, iv):
        # Custom bitwise transformation for HMAC key derivation
        # Requires attacker to replicate this logic to sign their own payloads
        return bytes([((x << 3 | x >> 5) ^ 0x4B) & 0xFF for x in iv])

    def encrypt(self, iv, data):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        checksum = hashlib.sha256(data).hexdigest()[:16]
        payload = json.dumps({"d": data.decode(), "c": checksum}).encode()
        # ISO/IEC 9797-1 Padding Method 2 (0x80 then 0x00s)
        padding_len = 16 - (len(payload) % 16)
        padded = payload + b'\x80' + b'\x00' * (padding_len - 1)
        return cipher.encrypt(padded)

    def _finalize_validation_cycle(self, block):
        # Subtle timing side-channel logic: no explicit comments identifying it
        # Increased iterations for a more stable timing signature
        state = hashlib.sha384(block).digest()
        for _ in range(480000):
            state = hashlib.sha384(state).digest()
        return state

    def process_frame(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        if not decrypted:
            return False

        # Verify ISO/IEC 9797-1 Method 2 Padding
        idx = len(decrypted) - 1
        while idx >= 0 and decrypted[idx] == 0:
            idx -= 1
        
        # Side-channel Oracle: If padding check fails, return immediately (fast)
        if idx < 0 or decrypted[idx] != 0x80:
            return False

        # Success Path: Only reached if padding is valid (slow)
        self._finalize_validation_cycle(decrypted)
        
        try:
            raw_data = decrypted[:idx]
            payload = json.loads(raw_data.decode())
            data = payload.get('d', '')
            checksum = payload.get('c', '')
            expected_checksum = hashlib.sha256(data.encode()).hexdigest()[:16]
            return hmac.compare_digest(checksum, expected_checksum)
        except:
            return False