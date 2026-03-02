import os
import json
import hmac
import hashlib
import time
import random
import base64
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

def _derive_integrity_key(master_key):
    # Hardened key derivation: involves bitwise rotation and constant folding
    # to make manual reversal more tedious.
    def rotr8(val, n):
        return ((val & 0xff) >> n | (val << (8 - n))) & 0xff
    
    derived = bytearray(master_key)
    const = b"SGC_FW_v2.0.42_STABLE"
    for i in range(len(derived)):
        derived[i] = rotr8(derived[i], 3) ^ const[i % len(const)]
    
    return hashlib.pbkdf2_hmac('sha256', derived, b"SGC_SALT_2024", 5000)

def _compute_internal_cycles(raw_data):
    # Hardened side-channel: Removed graduated leak. 
    # Now uses binary signals buried in heavy Gaussian-like noise.
    # Attacker must use statistical averaging to distinguish the signal.
    
    base_cycles = 0x4B0 # 1200
    signal = 0
    
    # X9.23 Padding Oracle Logic (Strict Binary)
    if len(raw_data) % 16 == 0 and len(raw_data) > 0:
        pad_len = raw_data[-1]
        if 1 <= pad_len <= 16:
            valid_padding = True
            for i in range(2, pad_len + 1):
                if raw_data[-i] != 0:
                    valid_padding = False
                    break
            
            if valid_padding:
                # Signal 1: Correct Padding
                signal += 150 
                
                try:
                    # Stage 2: Strict UTF-16BE Validation
                    plaintext = raw_data[:-pad_len].decode('utf-16be')
                    # Signal 2: Correct Encoding
                    signal += 150
                    
                    # Stage 3: Schema Validation
                    if '"action":' in plaintext:
                        # Signal 3: Correct Schema
                        signal += 200
                except UnicodeDecodeError:
                    pass
    
    # Add significant jitter to prevent single-shot oracle exploitation
    # Standard deviation is high enough that multiple samples are required
    jitter = sum(random.randint(-25, 25) for _ in range(5))
    return base_cycles + signal + jitter

def load_challenge():
    try:
        with open('key.bin', 'rb') as f:
            key = f.read()
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
        return key, data['iv'], data['encrypted_flag']
    except Exception:
        return os.urandom(16), os.urandom(16).hex(), ""

SECRET_KEY, SYSTEM_IV, ENCRYPTED_FLAG = load_challenge()
INTEGRITY_KEY = _derive_integrity_key(SECRET_KEY)

@app.route('/api/v1/telemetry/archive', methods=['GET'])
def get_archive():
    return jsonify({
        "packet_id": f"SGC-LOG-{random.getrandbits(32)}",
        "status": "ARCHIVED",
        "iv": SYSTEM_IV,
        "payload": ENCRYPTED_FLAG
    })

@app.route('/api/v1/command/verify', methods=['POST'])
def verify_command():
    try:
        data = request.get_json()
        token = request.headers.get('X-SGC-Integrity-Token')

        if not data or 'iv' not in data or 'payload' not in data or not token:
            return jsonify({"error": "Access Denied", "reason": "AUTH_MISSING"}), 401

        # Verify HMAC with the hardened derived key
        raw_body = (data['iv'] + data['payload']).encode()
        expected_mac = hmac.new(INTEGRITY_KEY, raw_body, hashlib.sha256).digest()
        if not hmac.compare_digest(base64.b64decode(token), expected_mac):
            # Timing penalty for failed MAC to deter brute forcing
            time.sleep(0.1)
            return jsonify({"error": "Access Denied", "reason": "MAC_FAILURE"}), 403

        iv = bytes.fromhex(data['iv'])
        payload = bytes.fromhex(data['payload'])
        
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(payload)
        
        cycle_count = _compute_internal_cycles(decrypted)
        
        # Real-world network simulation jitter
        time.sleep(random.uniform(0.01, 0.03))
        
        return jsonify({
            "status": "PROCESSED",
            "metrics": {
                "cycle_count": cycle_count,
                "bus_load": round(cycle_count / 15000.0, 6)
            }
        }), 200

    except Exception:
        return jsonify({"status": "FAULT", "error": "BUS_ERROR"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)