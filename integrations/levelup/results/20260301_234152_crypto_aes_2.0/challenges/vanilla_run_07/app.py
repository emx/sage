import os
import struct
import json
import time
import random
from flask import Flask, request, jsonify
from crypto_utils import SkyLinkCrypto

app = Flask(__name__)

# Load the master key from the generated file
VAULT_KEY_PATH = 'vault.key'
try:
    with open(VAULT_KEY_PATH, 'rb') as f:
        MASTER_KEY = f.read()
except FileNotFoundError:
    MASTER_KEY = b'\x00' * 16

crypto = SkyLinkCrypto(MASTER_KEY)

@app.route('/api/vault/archive/latest', methods=['GET'])
def get_latest_archive():
    try:
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
        return jsonify({
            "status": "archived",
            "drone_id": "STRAT9-ALPHA",
            "payload_hex": data['encrypted_flag'],
            "iv_hex": data['iv'],
            "version": "2.0.4-STABLE"
        })
    except Exception as e:
        return jsonify({"error": "Vault index unavailable"}), 500

@app.route('/api/vault/telemetry/verify', methods=['POST'])
def verify_telemetry():
    # Add artificial jitter to make timing analysis slightly more realistic
    time.sleep(random.uniform(0.002, 0.008))
    
    req_data = request.get_json()
    if not req_data or 'iv' not in req_data or 'payload' not in req_data:
        return jsonify({"error": "Malformed request"}), 400

    try:
        iv = bytes.fromhex(req_data['iv'])
        ct = bytes.fromhex(req_data['payload'])
        
        if len(iv) != 16:
            return jsonify({"error": "Invalid IV length"}), 400

        # Unified response prevents textbook error-based padding oracle
        # The oracle is now timing-based (injected in crypto_utils)
        result, _ = crypto.verify_packet(iv, ct)
        
        if result:
            return jsonify({"status": "SUCCESS", "message": "Telemetry verified and synced."}), 200
        else:
            # Generic error code for all failure types
            return jsonify({"status": "ERROR", "code": "ERR_REJECTED"}), 400

    except Exception as e:
        return jsonify({"error": "Internal processing error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)