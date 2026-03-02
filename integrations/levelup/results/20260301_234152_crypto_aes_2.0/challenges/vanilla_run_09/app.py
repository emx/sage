import os
import json
import hashlib
from flask import Flask, request, jsonify
from crypto_utils import AESOracle

app = Flask(__name__)

# Oracle salt is fixed per session, but response includes a rotating window
ORACLE_SALT = os.urandom(24).hex()
REQUEST_COUNT = 0

def load_data():
    try:
        with open('challenge_data.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {}

CHALLENGE_DATA = load_data()
ORACLE = AESOracle(CHALLENGE_DATA.get('key')) if CHALLENGE_DATA.get('key') else None

@app.route('/api/telemetry/archive', methods=['GET'])
def get_archive():
    return jsonify({
        "status": "success",
        "description": "Solstice-1 Archival Telemetry Segment (Deep Space Hardened)",
        "iv": CHALLENGE_DATA.get('iv'),
        "ciphertext": CHALLENGE_DATA.get('ciphertext')
    })

@app.route('/api/telemetry/verify', methods=['POST'])
def verify_telemetry():
    global REQUEST_COUNT
    if not ORACLE:
        return jsonify({"status": "error", "message": "Oracle not initialized"}), 500

    data = request.get_json()
    if not data or 'ciphertext' not in data or 'iv' not in data:
        return jsonify({"status": "error", "message": "Malformed request"}), 400

    try:
        ct = bytes.fromhex(data['ciphertext'])
        iv = bytes.fromhex(data['iv'])
        
        # Oracle returns:
        # 0: Success (Padding + Integrity OK)
        # 1: Padding Error
        # 2: Structural/Integrity Error
        result_code = ORACLE.decrypt_and_verify(ct, iv)
        
        # HARDENING: Salt rotation every 8 requests.
        # The attacker must synchronize their oracle mapping within a small window.
        window = REQUEST_COUNT // 8
        response_sig = hashlib.sha256(f"{ORACLE_SALT}{result_code}{window}".encode()).hexdigest()
        
        REQUEST_COUNT += 1
        
        return jsonify({
            "status": "processed",
            "verification_token": response_sig,
            "request_id": REQUEST_COUNT - 1
        })
            
    except Exception as e:
        return jsonify({"status": "error", "message": "Processing failure"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)