import os
import json
import hashlib
import hmac
import time
from flask import Flask, request, jsonify
from crypto_utils import ValkyrieCipher

app = Flask(__name__)

def load_challenge():
    try:
        if os.path.exists('challenge_data.json'):
            with open('challenge_data.json', 'r') as f:
                return json.load(f)
    except Exception:
        return None
    return None

DATA = load_challenge()
CIPHER = ValkyrieCipher(bytes.fromhex(DATA['key'])) if DATA and 'key' in DATA else None

@app.route('/api/vault/status', methods=['GET'])
def status():
    return jsonify({
        "status": "operational",
        "module": "Valkyrie Telemetry Vault",
        "firmware": "2.6.1-hardened-enterprise"
    })

@app.route('/api/vault/telemetry', methods=['GET'])
def get_telemetry():
    if not DATA:
        return jsonify({"error": "System not initialized"}), 500
    return jsonify({
        "mission": "Valkyrie-Actual",
        "iv": DATA['iv'],
        "payload": DATA['ciphertext']
    })

@app.route('/api/vault/verify', methods=['POST'])
def verify_telemetry():
    if not CIPHER:
        return jsonify({"error": "System not initialized"}), 500

    req_data = request.get_json()
    if not req_data or 'iv' not in req_data or 'payload' not in req_data:
        return jsonify({"status": "error", "code": "MALFORMED_REQUEST"}), 400

    sig = request.headers.get('X-Valkyrie-Signature')
    try:
        iv_bytes = bytes.fromhex(req_data['iv'])
        payload_bytes = bytes.fromhex(req_data['payload'])
        
        # HMAC key is derived through a non-obvious transformation in crypto_utils
        derived_key = CIPHER.derive_internal_token(iv_bytes)
        expected_sig = hmac.new(derived_key, payload_bytes, hashlib.sha256).hexdigest()
    except Exception as e:
        return jsonify({"status": "error", "code": "SIGNATURE_FAILURE"}), 400

    if not sig or not hmac.compare_digest(sig, expected_sig):
        return jsonify({"status": "error", "code": "ACCESS_DENIED"}), 403

    # result is True only if padding AND internal checksum pass
    result = CIPHER.process_frame(iv_bytes, payload_bytes)

    if result:
        return jsonify({"status": "success", "message": "Telemetry verified and synced."})
    else:
        return jsonify({"status": "error", "code": "SIGNAL_LOST"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)