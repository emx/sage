import os
import json
import hashlib
import datetime
import time
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from crypto_utils import verify_pow

app = Flask(__name__)

# Load encrypted challenge data
with open('challenge_data.json', 'r') as f:
    data = json.load(f)
    ENCRYPTED_FLAG = data['ciphertext']
    INITIAL_IV = data['iv']

# Load secret key
with open('secret.key', 'rb') as f:
    SECRET_KEY = f.read()

@app.route('/api/telemetry/archive', methods=['GET'])
def get_archive():
    """Returns the encrypted mission logs for analysis."""
    return jsonify({
        "status": "success",
        "module": "BlackBox_v2.5_Stable",
        "telemetry_id": "A9-TRK-7721-B",
        "iv": INITIAL_IV,
        "data": ENCRYPTED_FLAG,
        "pow_difficulty": 20
    })

@app.route('/api/telemetry/verify', methods=['POST'])
def verify_telemetry():
    """Oracle endpoint for DSAS integrity verification."""
    start_time = time.time()
    req_data = request.get_json()
    if not req_data or 'data' not in req_data or 'iv' not in req_data or 'nonce' not in req_data:
        return jsonify({"error": "Invalid request format"}), 400

    ciphertext_hex = req_data['data']
    iv_hex = req_data['iv']
    nonce_hex = req_data['nonce']

    # Requirement: Hardened Proof of Work (20-bit)
    # Now requires ciphertext + iv in the hash to prevent replay and pre-computation
    if not verify_pow(iv_hex, ciphertext_hex, nonce_hex):
        return jsonify({"error": "PoW verification failed", "required": "20-bit prefix"}), 403

    try:
        ct = bytes.fromhex(ciphertext_hex)
        iv = bytes.fromhex(iv_hex)
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ct)
        
        now = datetime.datetime.utcnow()
        # Subtly differing response patterns based on decryption state
        try:
            # Check PKCS7 Padding
            plaintext = unpad(decrypted, 16)
            
            # Check DSAS Integrity Header
            if not plaintext.startswith(b'ASTRA9_LOG_V2.5:'):
                # Padding valid, but header invalid
                # Oracle signal: Microsecond precision timestamp
                res = jsonify({"status": "error", "message": "Verification failure", "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.%f")})
            else:
                # Success case
                res = jsonify({"status": "success", "message": "Block verified", "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S.%f")})
            
        except ValueError:
            # Padding invalid
            # Oracle signal: Millisecond precision timestamp (truncated)
            ms_ts = now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}"
            res = jsonify({"status": "error", "message": "Verification failure", "timestamp": ms_ts})
            
    except Exception:
        return jsonify({"status": "error", "message": "Internal processing error"}), 500

    # Constant-time delay to mitigate basic timing attacks and force reliance on the subtle oracle
    duration = time.time() - start_time
    time.sleep(max(0, 0.02 - duration))
    return res, 400 if "error" in res.get_json().get("status", "error") else 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)