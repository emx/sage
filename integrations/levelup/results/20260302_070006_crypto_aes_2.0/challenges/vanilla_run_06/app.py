import os
import json
import time
import hmac
import hashlib
import random
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

class HorizonCipher:
    def __init__(self, key):
        self.key = key

    def derive_integrity_key(self, iv):
        return hmac.new(self.key, iv, hashlib.sha256).digest()

    def _security_scrub(self, data):
        # Computational decoy to add CPU-bound noise and increase base latency
        # This makes timing analysis harder by adding variance in system scheduling
        state = hashlib.sha512(data)
        for _ in range(2500):
            state = hashlib.sha512(state.digest())
        return state.digest()

    def verify_integrity(self, iv, ciphertext):
        # Standard AES-CBC Decryption
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # ISO 10126 Padding Verification
        # In ISO 10126, only the last byte (length) is strictly defined for validation
        pad_len = decrypted[-1]
        is_valid_padding = 1 <= pad_len <= 16
        
        is_valid_mac = False
        if is_valid_padding:
            unpadded = decrypted[:-pad_len]
            if len(unpadded) >= 32:
                payload = unpadded[:-32]
                received_mac = unpadded[-32:]
                integrity_key = self.derive_integrity_key(iv)
                calculated_mac = hmac.new(integrity_key, payload, hashlib.sha256).digest()
                is_valid_mac = hmac.compare_digest(received_mac, calculated_mac)
        
        return is_valid_padding, is_valid_mac, pad_len

app = Flask(__name__)

with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

with open('telemetry.key', 'rb') as f:
    SECRET_KEY = f.read()

CIPHER = HorizonCipher(SECRET_KEY)

@app.route('/api/telemetry/status', methods=['GET'])
def get_status():
    return jsonify({
        "gateway_id": "HG-PNW-01",
        "status": "OPERATIONAL",
        "admin_packet": CHALLENGE_DATA['admin_packet'],
        "note": "Admin stream is currently encrypted for secure transit."
    })

@app.route('/api/telemetry/diagnostics', methods=['POST'])
def diagnostics():
    try:
        data = request.json.get('payload')
        if not data:
            return jsonify({"status": "error"}), 400
        
        payload_bytes = bytes.fromhex(data)
        if len(payload_bytes) < 48:
            return jsonify({"status": "error"}), 400

        # Constant computational overhead
        CIPHER._security_scrub(payload_bytes)

        iv = payload_bytes[:16]
        ciphertext = payload_bytes[16:]
        
        is_valid_padding, is_valid_mac, pad_len = CIPHER.verify_integrity(iv, ciphertext)
        
        # HARDENED TIMING ORACLE
        # The signal is now much smaller (approx 4ms) compared to high noise (10ms).
        # Furthermore, the signal varies based on the padding length, preventing
        # simple binary classification without significant statistical sampling.
        
        # Base noise floor: 8ms to 18ms
        noise = random.uniform(0.008, 0.018)
        
        if is_valid_padding:
            # Signal: 4ms base + 0.2ms per pad byte
            signal = 0.004 + (pad_len * 0.0002)
            time.sleep(noise + signal)
        else:
            time.sleep(noise)

        if not (is_valid_padding and is_valid_mac):
            return jsonify({"status": "error", "msg": "Authentication failure"}), 403
            
        return jsonify({"status": "ok", "message": "Packet synchronized successfully"})

    except Exception:
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)