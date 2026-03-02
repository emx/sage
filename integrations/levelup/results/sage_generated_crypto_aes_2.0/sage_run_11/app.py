import os
import json
import hashlib
import time
from flask import Flask, request, jsonify, make_response
from crypto_utils import StratosCipher, get_service_key

app = Flask(__name__)

# Global request tracker to prevent trivial automation and replay attacks
# Forces attackers to provide unique Request-IDs for salt-based signatures
USED_REQUESTS = set()
MAX_TRACKED = 10000

SERVICE_KEY = get_service_key()
cipher_suite = StratosCipher(SERVICE_KEY)

with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

@app.route('/api/telemetry/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "status": "success",
        "vault_id": "STRATOS-VAULT-01",
        "manifest_enc": CHALLENGE_DATA['encrypted_flag'],
        "frame_id": CHALLENGE_DATA['frame_id']
    })

@app.route('/api/telemetry/upload', methods=['POST'])
def upload_telemetry():
    global USED_REQUESTS
    data = request.get_json()
    frame_id = request.headers.get('X-Frame-ID')
    rid = request.headers.get('X-Request-ID')
    
    if not data or 'payload' not in data or not frame_id or not rid:
        return jsonify({"error": "Missing parameters or security headers"}), 400
    
    # Security: Request ID must be unique to prevent replay-based oracle calibration
    if rid in USED_REQUESTS:
        return jsonify({"error": "Duplicate Request-ID detected"}), 403
    
    USED_REQUESTS.add(rid)
    if len(USED_REQUESTS) > MAX_TRACKED:
        USED_REQUESTS.clear()

    try:
        payload_bytes = bytes.fromhex(data['payload'])
        # The oracle signal now depends on multiple stages: padding, encoding, and logic
        decrypted_data = cipher_suite.decrypt(payload_bytes, frame_id)
        
        if decrypted_data is None:
            # Stage 1: Padding failure
            status = "P_ERR"
        else:
            try:
                # Stage 2: UTF-8 Encoding validation
                decoded = decrypted_data.decode('utf-8')
                # Stage 3: Logical Structure (Must start with JSON object marker)
                if decoded.startswith('{'):
                    status = "SUCCESS"
                else:
                    status = "C_ERR"
            except UnicodeDecodeError:
                status = "C_ERR"

        # Graduated Oracle: Signature is salted by the Request-ID provided by the user
        # This makes the oracle non-binary and prevents standard tools from using static signatures.
        oracle_seed = f"{rid}:{status}".encode()
        sig = hashlib.sha256(oracle_seed).hexdigest()
        
        # Add minor timing noise to frustrate simplistic automation scripts
        time.sleep(0.005)
        
        resp = make_response(jsonify({"status": "error", "msg": "Analysis failed"}), 200)
        resp.headers['X-Analysis-Sig'] = sig
        return resp
            
    except Exception as e:
        return jsonify({"error": "Internal Processing Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)