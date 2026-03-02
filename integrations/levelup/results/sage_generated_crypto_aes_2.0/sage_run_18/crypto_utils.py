from Crypto.Cipher import AES
import hashlib
import time

class DSASManager:
    def __init__(self, key):
        self.key = key

    def _rotate_iv(self, iv):
        # Bijective transformation: Circular bit shift left by 1 per byte
        return bytes([((b << 1) & 0xFF) | (b >> 7) for b in iv])

    def verify(self, iv_provided, ciphertext):
        try:
            # IV is transformed before use, preventing simple bit-flipping on block 0
            real_iv = self._rotate_iv(iv_provided)
            cipher = AES.new(self.key, AES.MODE_CBC, real_iv)
            plaintext = cipher.decrypt(ciphertext)
        except Exception:
            return "ERR"

        # 1. Position-Dependent Interleaved Padding Check
        # Instead of P, P, P... it uses P^1, P^2, P^3...
        padding_valid = True
        try:
            last_byte = plaintext[-1]
            pad_len = last_byte ^ (1) # Expected pad_len ^ index_from_end
            if pad_len < 1 or pad_len > 16:
                padding_valid = False
            else:
                for i in range(1, pad_len + 1):
                    if plaintext[-i] != (pad_len ^ i):
                        padding_valid = False
                        break
        except Exception:
            padding_valid = False

        if not padding_valid:
            # Return immediately on padding failure
            return "ERR_PAD"

        # 2. Timing Side-Channel (Heavy Integrity Check)
        # If padding is valid, we perform a computationally expensive check.
        # This allows a Timing-based Padding Oracle attack.
        # 10,000 rounds of PBKDF2 takes ~15-25ms.
        hashlib.pbkdf2_hmac('sha256', plaintext, b'dsas_salt_v8', 10000)

        # 3. Logic Check
        unpadded = plaintext[:-pad_len]
        if not unpadded.startswith(b"VA-MV7|"):
            return "ERR_LOGIC"

        return "OK_000"