import os
import json
import hashlib
import hmac
import time
import random
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# Load pre-generated key and encrypted data
with open('secret.key', 'rb') as f:
    AES_KEY = f.read()

with open('mask.bin', 'rb') as f:
    IV_MASK = f.read()

with open('challenge_data.json', 'r') as f:
    challenge_data = json.load(f)
    ENCRYPTED_RECORD = challenge_data['encrypted_flag']

class IcarusCipher:
    def __init__(self, key):
        self.key = key

    def decrypt_with_padding_check(self, iv, ciphertext):
        # Apply the hardware-level IV masking
        actual_iv = bytes([a ^ b for a, b in zip(iv, IV_MASK)])
        cipher = AES.new(self.key, AES.MODE_CBC, actual_iv)
        pt = cipher.decrypt(ciphertext)
        
        # Manual PKCS7 padding validation
        if len(pt) == 0:
            return None, False
        
        pad_len = pt[-1]
        if pad_len < 1 or pad_len > 16:
            return None, False
        
        for i in range(1, pad_len + 1):
            if pt[-i] != pad_len:
                return None, False
        
        return pt[:-pad_len], True

cipher_service = IcarusCipher(AES_KEY)

@app.route('/api/v1/telemetry/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "OPERATIONAL",
        "system": "Project Icarus Telemetry Bridge",
        "archived_record": ENCRYPTED_RECORD,
        "config": {
            "mode": "AES-CBC",
            "iv_processing": "XOR_MASKED",
            "auth": "HMAC_SHA256_REQUIRED",
            "pow_difficulty": 3
        }
    })

@app.route('/api/v1/telemetry/verify', methods=['POST'])
def verify_telemetry():
    data = request.json
    token = request.headers.get('X-Icarus-Token')
    nonce = request.headers.get('X-Icarus-Nonce')
    
    if not data or 'iv' not in data or 'ct' not in data or not token or not nonce:
        return jsonify({"status": "rejected", "error": {"code": 400, "message": "Malformed request"}}), 400

    try:
        iv = bytes.fromhex(data['iv'])
        ct = bytes.fromhex(data['ct'])
        
        # Layer 1: Proof-of-Work to prevent brute-force without computational cost
        # Nonce must make sha256(iv + nonce) start with '000'
        pow_check = hashlib.sha256(iv + nonce.encode()).hexdigest()
        if not pow_check.startswith('000'):
            return jsonify({"status": "rejected", "error": {"code": 401, "message": "Invalid proof-of-work"}}), 401

        # Layer 2: Keyed Token Verification
        # Attacker can compute this, but it requires aligning the nonce and IV correctly
        expected_token = hmac.new(nonce.encode(), iv, hashlib.sha256).hexdigest()
        if token != expected_token:
            return jsonify({"status": "rejected", "error": {"code": 401, "message": "Authentication failure"}}), 401

        # Start timing for the oracle
        start_time = time.time()

        plaintext, padding_valid = cipher_service.decrypt_with_padding_check(iv, ct)

        # The oracle is now BLIND. Both errors return code 400 with the exact same message.
        # The only differentiator is the processing time.
        base_delay = 0.02 + random.uniform(0, 0.005) # Small jitter to mask raw processing

        if padding_valid:
            # If padding is valid, verify logical prefix
            if plaintext.startswith(b"ICARUS_REC:"):
                return jsonify({"status": "Verified", "checksum": hashlib.sha1(plaintext).hexdigest()}), 200
            else:
                # Correct padding but wrong content: Add a significant delay (Timing Oracle Signal)
                base_delay += 0.08

        # Blind response after calibrated delay
        elapsed = time.time() - start_time
        if elapsed < base_delay:
            time.sleep(base_delay - elapsed)

        return jsonify({"status": "rejected", "error": {"code": 400, "message": "Signal integrity failure"}}), 400

    except Exception as e:
        return jsonify({"status": "rejected", "error": {"code": 500, "message": "Internal system fault"}}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)