import os
import hmac
import hashlib
from Crypto.Cipher import AES

def get_service_key():
    try:
        with open('secret.key', 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return b'\x00' * 16

class StratosCipher:
    def __init__(self, key):
        self.key = key

    def get_iv(self, frame_id):
        return hmac.new(self.key, frame_id.encode(), hashlib.sha256).digest()[:16]

    def pad_inverted_iso(self, data, block_size=16):
        # Hardened Padding: Bit-Inverted ISO/IEC 7816-4 (0x7F then 0xFFs)
        pad_len = block_size - (len(data) % block_size)
        return data + b'\x7f' + (b'\xff' * (pad_len - 1))

    def unpad_inverted_iso(self, data):
        # Strict unpadding for the inverted scheme
        i = len(data) - 1
        while i >= 0 and data[i] == 0xff:
            i -= 1
        if i >= 0 and data[i] == 0x7f:
            return data[:i]
        raise ValueError("Invalid padding")

    def encrypt(self, plaintext, frame_id):
        iv = self.get_iv(frame_id)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded = self.pad_inverted_iso(plaintext)
        ct = cipher.encrypt(padded)
        return ct.hex()

    def decrypt(self, ct_bytes, frame_id):
        try:
            iv = self.get_iv(frame_id)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt_padded = cipher.decrypt(ct_bytes)
            return self.unpad_inverted_iso(pt_padded)
        except:
            return None