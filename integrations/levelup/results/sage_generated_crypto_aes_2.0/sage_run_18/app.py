import os
import json
import time
import hashlib
import hmac
from flask import Flask, request, jsonify
from crypto_utils import DSASManager

app = Flask(__name__)

DATA_FILE = 'challenge_data.json'
KEY_FILE = 'vault.key'

try:
    with open(DATA_FILE, 'r') as f:
        challenge_params = json.load(f)
    with open(KEY_FILE, 'rb') as f:
        VAULT_KEY = f.read()
except FileNotFoundError:
    VAULT_KEY = os.urandom(32)
    challenge_params = {"iv": "0"*32, "encrypted_manifest": "0"*32, "epoch": int(time.time())}

dsas = DSASManager(VAULT_KEY)

@app.route('/')
def index():
    return jsonify({
        "service": "Manifest-Vault 8-Enterprise",
        "status": "Operational",
        "security_policy": "Strict-PoW-Required",
        "endpoints": {
            "/api/manifest/logs": "GET - Retrieve encrypted manifest bundle and PoW challenge",
            "/api/manifest/validate": "POST - Validate manifest (Required: data, iv, nonce)"
        }
    })

@app.route('/api/manifest/logs', methods=['GET'])
def get_logs():
    # The epoch serves as a salt for the Proof-of-Work to prevent pre-computation
    epoch = int(time.time())
    return jsonify({
        "status": "authorized",
        "manifest_bundle": {
            "iv": challenge_params["iv"],
            "data": challenge_params["encrypted_manifest"],
            "pow_difficulty": 3,
            "epoch": epoch
        }
    })

@app.route('/api/manifest/validate', methods=['POST'])
def validate_manifest():
    req_data = request.get_json()
    if not req_data or not all(k in req_data for k in ('data', 'iv', 'nonce', 'epoch')):
        return jsonify({"status": "error", "reason": "Missing Parameters"}), 400

    # 1. Proof of Work Verification (Anti-Automation)
    # nonce must result in sha256(nonce + epoch) starting with '000'
    pow_input = f"{req_data['nonce']}{req_data['epoch']}".encode()
    pow_hash = hashlib.sha256(pow_input).hexdigest()
    if not pow_hash.startswith('000'):
        return jsonify({"status": "error", "reason": "Invalid Security Token"}), 400

    try:
        iv = bytes.fromhex(req_data['iv'])
        ciphertext = bytes.fromhex(req_data['data'])
        if len(iv) != 16:
            return jsonify({"status": "error", "reason": "Parameter Mismatch"}), 400
    except Exception:
        return jsonify({"status": "error", "reason": "Encoding Error"}), 400

    # 2. Cryptographic Processing
    # The DSAS core is now hardened against direct error codes.
    # It uses a timing side-channel for padding validation.
    start_time = time.time()
    
    # Constant base delay to prevent network jitter noise
    time.sleep(0.02)

    result = dsas.verify(iv, ciphertext)
    
    # Total processing time is leaked through the DSAS verify method's heavy integrity check
    # If result is SUCCESS, returns 200.
    # If result is any error, return a UNIFIED 400 response.
    # The attacker must use the timing delta to differentiate Padding Error vs Logic Error.
    
    if result == "OK_000":
        return jsonify({"status": "success", "info": "Integrity Verified"}), 200
    else:
        return jsonify({"status": "error", "reason": "Validation Failed"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)