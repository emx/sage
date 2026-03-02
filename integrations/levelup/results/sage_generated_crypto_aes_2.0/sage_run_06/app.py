import os
import json
import hashlib
import hmac
import time
from flask import Flask, request, jsonify
from crypto_utils import decrypt_and_verify_dsas

app = Flask(__name__)

# Load pre-generated challenge data
with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

with open('archival.key', 'rb') as f:
    ARCHIVAL_KEY = f.read()

def get_oracle_tid(status, iv):
    """Generates a deterministic but non-obvious transaction ID as a side-channel."""
    ctx = hashlib.sha256()
    ctx.update(status.encode())
    ctx.update(iv)
    # Return a 16-character hex string as a 'unique' ID
    return ctx.hexdigest()[:16]

@app.route('/api/v1/archive/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify({
        "description": "Encrypted Project Horizon Telemetry Blob",
        "blob": CHALLENGE_DATA['encrypted_blob'],
        "iv": CHALLENGE_DATA['iv'],
        "sample_pow": CHALLENGE_DATA['sample_pow']
    })

@app.route('/api/v1/archive/verify', methods=['POST'])
def verify_telemetry():
    data = request.json
    if not data or 'iv' not in data or 'data' not in data or 'pow' not in data:
        return jsonify({"status": "error", "message": "Malformed Request"}), 200

    # 20-bit Proof of Work requirement
    pow_nonce = str(data['pow'])
    if not hashlib.sha256(pow_nonce.encode()).hexdigest().startswith('00000'):
        return jsonify({"status": "error", "message": "Access Denied: PoW Failure"}), 403

    try:
        iv = bytes.fromhex(data['iv'])
        ciphertext = bytes.fromhex(data['data'])
        
        if len(iv) != 16:
            return jsonify({"status": "error", "message": "Invalid Parameter Size"}), 200

        # The oracle is now hidden in the 'tid' field of a successful-looking response.
        # All errors return status 200 to neutralize status-code based automation.
        status_code = decrypt_and_verify_dsas(ARCHIVAL_KEY, iv, ciphertext, pow_nonce)
        
        # Timing jitter to prevent trivial timing analysis
        time.sleep(0.01)
        
        if status_code == "SUCCESS":
            return jsonify({
                "status": "processed", 
                "tid": get_oracle_tid("SUCCESS", iv), 
                "message": "Telemetry integrity verified"
            }), 200
        else:
            # The specific error (PAD, MAGIC, or JSON) is distinguishable ONLY by the tid
            return jsonify({
                "status": "processed", 
                "tid": get_oracle_tid(status_code, iv), 
                "message": "Processing complete: Integrity check failed"
            }), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": "Internal processing error"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)