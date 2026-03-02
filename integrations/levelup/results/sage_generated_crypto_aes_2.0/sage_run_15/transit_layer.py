import os
import struct
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

class TransitError(Exception):
    pass

class SecureTransit:
    def __init__(self, key):
        self.key = key
        self.salt = b"\xde\xad\xbe\xef\x13\x37"

    def _fib(self, n):
        if n <= 0: return 0
        if n == 1: return 1
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a % 256

    def _get_block_mask(self, idx):
        # Derive a positional mask to prevent block swapping/replays
        # Uses PBKDF2 to increase the cost of automated brute forcing
        return PBKDF2(self.key, self.salt + struct.pack("<I", idx), 16, count=50, hmac_hash_module=SHA256)

    def encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_ECB)
        
        # Fibonacci Padding: P[-1]=L, P[-i]=L^fib(i-1)
        pad_len = 16 - (len(data) % 16)
        padding = bytes([pad_len ^ self._fib(i) for i in range(pad_len - 1, -1, -1)])
        padded_data = data + padding
        
        blocks = [padded_data[i:i+16] for i in range(0, len(padded_data), 16)]
        ciphertext = b""
        prev_ct = iv
        
        for idx, block in enumerate(blocks):
            # Hardened CBC: C_i = E( (P_i ^ C_{i-1}) ^ K_i )
            k_i = self._get_block_mask(idx)
            shifted = bytes([b ^ c for b, c in zip(block, prev_ct)])
            to_encrypt = bytes([s ^ k for s, k in zip(shifted, k_i)])
            curr_ct = cipher.encrypt(to_encrypt)
            ciphertext += curr_ct
            prev_ct = curr_ct
            
        return iv + ciphertext

    def decrypt(self, token: bytes) -> bytes:
        if len(token) < 32 or len(token) % 16 != 0:
            raise TransitError("ERR_FMT")
            
        iv = token[:16]
        ciphertext = token[16:]
        cipher = AES.new(self.key, AES.MODE_ECB)
        
        ct_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
        decrypted_payload = b""
        prev_ct = iv
        
        try:
            for idx, ct_block in enumerate(ct_blocks):
                k_i = self._get_block_mask(idx)
                raw_dec = cipher.decrypt(ct_block)
                # Reverse internal mask
                unshifted = bytes([r ^ k for r, k in zip(raw_dec, k_i)])
                # Reverse CBC XOR
                p_i = bytes([u ^ p for u, p in zip(unshifted, prev_ct)])
                decrypted_payload += p_i
                prev_ct = ct_block
                
            # Validate Fibonacci Padding
            l = decrypted_payload[-1]
            if l < 1 or l > 16:
                raise TransitError("ERR_PAD")
            
            for i in range(1, l + 1):
                if decrypted_payload[-i] != (l ^ self._fib(i-1)):
                    raise TransitError("ERR_PAD")
                    
            return decrypted_payload[:-l]
        except Exception:
            raise TransitError("ERR_SEC")