import os
import hashlib
from Crypto.Cipher import AES

class AESCipher:
    def __init__(self, key):
        self.key = key

    def _rotate_block(self, block, n=3):
        """Rotates bits in each byte of the block to the left by n."""
        return bytes([((b << n) | (b >> (8 - n))) & 0xFF for b in block])

    def pad_protocol(self, data, block_size=16):
        return data + b'\x80' + (b'\x00' * (block_size - len(data) % block_size - 1))

    def unpad_protocol(self, padded_data):
        idx = padded_data.rfind(b'\x80')
        if idx == -1: return None
        if any(b != 0 for b in padded_data[idx + 1:]): return None
        return padded_data[:idx]

    def encrypt(self, data):
        iv = os.urandom(16)
        padded = self.pad_protocol(data)
        cipher = AES.new(self.key, AES.MODE_ECB)
        ct = bytearray()
        prev = iv
        for i in range(0, len(padded), 16):
            block = padded[i:i+16]
            # Modified CBC: C_i = E(P_i ^ Rot(C_{i-1}, 3))
            mixed = bytes([b ^ r for b, r in zip(block, self._rotate_block(prev))])
            curr_ct = cipher.encrypt(mixed)
            ct.extend(curr_ct)
            prev = curr_ct
        return (iv + ct).hex()

    def raw_decrypt(self, data):
        iv = data[:16]
        ct = data[16:]
        cipher = AES.new(self.key, AES.MODE_ECB)
        pt = bytearray()
        prev = iv
        for i in range(0, len(ct), 16):
            block = ct[i:i+16]
            decrypted = cipher.decrypt(block)
            # P_i = D(C_i) ^ Rot(C_{i-1}, 3)
            pt.extend(bytes([d ^ r for d, r in zip(decrypted, self._rotate_block(prev))]))
            prev = block
        return bytes(pt)

class POWManager:
    def __init__(self, difficulty=6):
        self.difficulty = difficulty

    def generate_challenge(self):
        return os.urandom(8).hex()

    def verify(self, prefix, solution):
        if not prefix or not solution: return False
        h = hashlib.sha256((prefix + solution).encode()).hexdigest()
        return h.endswith('0' * self.difficulty)