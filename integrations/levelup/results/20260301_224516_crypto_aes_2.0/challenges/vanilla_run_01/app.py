import os
import json
import time
import random
import logging
import hashlib
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

SECRETS_PATH = 'secrets.json'
MANIFEST_PATH = 'challenge_data.json'

# Load configuration
try:
    with open(SECRETS_PATH, 'r') as f:
        secrets = json.load(f)
    AES_KEY = bytes.fromhex(secrets['key'])
except Exception:
    AES_KEY = os.urandom(16)

try:
    with open(MANIFEST_PATH, 'r') as f:
        manifest_data = json.load(f)
except Exception:
    manifest_data = {"iv": "0"*32, "ciphertext": "0"*32}

def _internal_integrity_verification(payload):
    """
    Performs a high-precision integrity check on decrypted payload.
    This operation introduces a subtle computational delay.
    """
    # 5ms deterministic delay to simulate complex validation logic
    # This is the timing side-channel for the padding oracle
    time.sleep(0.005)
    
    # Obfuscated checksum logic
    h = hashlib.sha256(payload).hexdigest()
    return h.startswith('00')

@app.route('/api/vault/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "iv": manifest_data.get('iv'),
        "ciphertext": manifest_data.get('ciphertext'),
        "info": "AetherFlow Orbital - NebulaVault Master Manifest v2.1 (Encrypted)"
    })

@app.route('/api/vault/telemetry/verify', methods=['POST'])
def verify_telemetry():
    # Enforce a base processing overhead to prevent high-speed brute forcing
    base_delay = 0.04
    time.sleep(base_delay)
    
    data = request.get_json()
    if not data or 'iv' not in data or 'ciphertext' not in data:
        return jsonify({"status": "error", "message": "Malformed request"}), 400

    # Standardized error response for all failure conditions
    error_res = (jsonify({"status": "error", "message": "Integrity check failed"}), 400)

    try:
        iv = bytes.fromhex(data['iv'])
        ct = bytes.fromhex(data['ciphertext'])
        
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ct)
        
        try:
            # PKCS7 Unpadding
            # If this succeeds, the execution takes ~5ms longer due to integrity check
            decrypted_data = unpad(decrypted, 16, style='pkcs7')
            
            # Perform the 'complex' validation that leaks padding success via timing
            _internal_integrity_verification(decrypted_data)
            
            # Obfuscated Format Check
            if decrypted_data.startswith(b"AetherFlow"):
                # Dynamic jitter to mask the side channel (2ms to 22ms)
                time.sleep(random.uniform(0.002, 0.022))
                return jsonify({"status": "success", "message": "Telemetry verified"}), 200
            else:
                time.sleep(random.uniform(0.002, 0.022))
                return error_res

        except (ValueError, KeyError):
            # Padding failed - exit immediately with jitter
            time.sleep(random.uniform(0.002, 0.022))
            return error_res

    except Exception:
        time.sleep(random.uniform(0.005, 0.025))
        return jsonify({"status": "error", "message": "System error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)