from Crypto.Cipher import AES
import json
import hmac
import hashlib

def horizon_unpad(plaintext):
    """Custom Horizon Padding: Modified ANSI X.923 with 0x42 XOR mask."""
    if not plaintext or len(plaintext) < 16:
        return None
    
    last_byte = plaintext[-1]
    pad_len = last_byte ^ 0x42
    
    if pad_len < 1 or pad_len > 16:
        return None
    
    # Check that all preceding bytes in the padding block are 0x42
    for i in range(2, pad_len + 1):
        if plaintext[-i] != 0x42:
            return None
            
    return plaintext[:-pad_len]

def decrypt_and_verify_dsas(key, iv, ciphertext, pow_nonce):
    """Multi-stage verification with IV transformation."""
    try:
        # The IV provided by the user is XORed with a session key K derived from the PoW.
        # K = HMAC(server_key, pow_nonce)
        h_iv = hmac.new(key, pow_nonce.encode(), hashlib.sha256).digest()
        actual_iv = bytes(a ^ b for a, b in zip(iv, h_iv[:16]))

        cipher = AES.new(key, AES.MODE_CBC, actual_iv)
        plaintext = cipher.decrypt(ciphertext)
    except:
        return "PAD"

    # Stage 1: Horizon Padding Check
    unpadded = horizon_unpad(plaintext)
    if unpadded is None:
        return "PAD"

    # Stage 2: Magic Header Check (Alignment Signature)
    if not unpadded.startswith(b'HZ\x01\x00'):
        return "MAGIC"

    # Stage 3: JSON Structural Check
    try:
        json.loads(unpadded[4:].decode('utf-8'))
        return "SUCCESS"
    except:
        return "JSON"
