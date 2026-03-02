import hashlib

def verify_pow(iv_hex, data_hex, nonce_hex):
    """Verifies a 20-bit Proof-of-Work (~1 million attempts per probe)."""
    try:
        # Difficulty increased and combined with request data to prevent reuse
        combined = (iv_hex + data_hex + nonce_hex).encode()
        h = hashlib.sha256(combined).hexdigest()
        # 20 bits = 5 hex characters
        return h.startswith('00000')
    except:
        return False