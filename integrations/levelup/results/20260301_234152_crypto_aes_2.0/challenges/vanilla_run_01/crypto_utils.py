from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import time

def verify_packet_integrity(payload_hex, key):
    try:
        data = bytes.fromhex(payload_hex)
        if len(data) < 32:
            return False
        
        iv = data[:16]
        ciphertext = data[16:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # Hardening: Transformation Layer
        # The plaintext is XORed with a mask derived from the IV's first byte
        # This requires the attacker to adjust their padding oracle math.
        mask = iv[0]
        transformed = bytes([b ^ mask for b in decrypted])
        
        try:
            # PKCS7 unpadding
            plaintext = unpad(transformed, 16)
            
            # SIDE CHANNEL: Explicit delay only if padding is valid.
            # This creates a timing oracle instead of an error-based oracle.
            time.sleep(0.06)
            
            if plaintext.startswith(b"VANGUARD_RELAY_v1.0:"):
                return True
            return False
        except ValueError:
            # Padding incorrect
            return False
    except Exception:
        return False