import os
import json
import uuid
import hashlib
import time
from flask import Flask, request, jsonify
from crypto_utils import AetherCipher

app = Flask(__name__)

SYSTEM_KEY_PATH = '/tmp/system.key'
if not os.path.exists(SYSTEM_KEY_PATH):
    SYSTEM_KEY = os.urandom(16)
else:
    with open(SYSTEM_KEY_PATH, 'rb') as f:
        SYSTEM_KEY = f.read()

cipher_suite = AetherCipher(SYSTEM_KEY)

# Session store to force stateful exploitation
sessions = {}

def check_pow(nonce, difficulty=4):
    h = hashlib.sha256(nonce.encode()).hexdigest()
    return h.startswith('0' * difficulty)

@app.route('/api/v1/auth/provision', methods=['POST'])
def provision():
    # Require simple PoW to prevent mindless spamming and force custom scripting
    req_data = request.get_json()
    nonce = req_data.get('nonce', '')
    if not check_pow(nonce):
        return jsonify({"error": "POW_FAILED", "hint": "SHA256(nonce) must start with '0000'"}), 403
    
    token = str(uuid.uuid4())
    sessions[token] = {"remaining": 50, "created": time.time()}
    return jsonify({"token": token, "limit": 50})

@app.route('/api/v1/telemetry/capture', methods=['GET'])
def capture_telemetry():
    try:
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
        
        return jsonify({
            "status": "success",
            "origin": "SAT-LOG-02",
            "payload": data['encrypted_flag'],
            "iv": data['iv'],
            "token_required": True
        })
    except Exception as e:
        return jsonify({"error": "Internal Bridge Fault"}), 500

@app.route('/api/v1/telemetry/verify', methods=['POST'])
def verify_telemetry():
    req_data = request.get_json()
    if not req_data or 'iv' not in req_data or 'payload' not in req_data or 'token' not in req_data:
        return jsonify({"error": "MALFORMED_REQUEST"}), 400

    token = req_data['token']
    if token not in sessions or sessions[token]['remaining'] <= 0:
        return jsonify({"error": "SESSION_EXPIRED"}), 403

    sessions[token]['remaining'] -= 1

    try:
        iv = bytes.fromhex(req_data['iv'])
        ct = bytes.fromhex(req_data['payload'])
        
        # Decryption depends on the session token for the dynamic scramble layer
        status_code = cipher_suite.decrypt_and_verify(ct, iv, token)
        
        if status_code == "SUCCESS":
            return jsonify({"status": "success", "code": 2000})
        elif status_code == "PADDING_ERR":
            # Oracle 1: Padding failure
            return jsonify({"status": "error", "code": 4001}), 400
        elif status_code == "INTEGRITY_ERR":
            # Oracle 2: Padding was correct, but checksum/header failed
            return jsonify({"status": "Error", "code": 4002}), 400
        else:
            return jsonify({"status": "error", "code": 5000}), 400

    except Exception as e:
        return jsonify({"error": "PROCESSING_FAULT"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)