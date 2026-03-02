from Crypto.Cipher import AES
import hashlib

class AESOracle:
    def __init__(self, key_hex):
        self.key = bytes.fromhex(key_hex) if key_hex else None

    def decrypt_and_verify(self, ciphertext, iv):
        if not self.key: return 1
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)
        
        # HARDENING: Non-linear IV-dependent padding
        # The padding value depends on the IV byte at a dynamic index.
        try:
            # Use the previous ciphertext block (or IV) to determine the padding mask
            # In CBC, the 'iv' passed here is the relevant XOR block for the current decryption.
            mask_idx = iv[15] % 16
            last_byte = plaintext[-1]
            pad_len = last_byte ^ iv[mask_idx]
            
            if pad_len < 1 or pad_len > 16:
                return 1
            
            for i in range(1, pad_len + 1):
                # Check each byte using a shifting IV index to prevent cancellation
                if (plaintext[-i] ^ iv[(16-i) % 16]) != pad_len:
                    return 1
            
            original_data = plaintext[:-pad_len]
        except Exception:
            return 1

        # Structural verification
        if original_data.startswith(b"AETHERIS-TLM:") and original_data.endswith(b":END"):
            return 0
        
        return 2