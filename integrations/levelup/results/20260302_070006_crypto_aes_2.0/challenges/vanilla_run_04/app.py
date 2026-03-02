import os
import json
import time
import random
import struct
import hashlib
from flask import Flask, request, jsonify, make_response
from crypto_utils import StellarCipher, SecurityEngine

app = Flask(__name__)

# Load encrypted challenge data
DATA_PATH = 'challenge_data.json'
KEY_PATH = 'vault.key'

with open(DATA_PATH, 'r') as f:
    challenge_data = json.load(f)

with open(KEY_PATH, 'rb') as f:
    VAULT_KEY = f.read()

engine = SecurityEngine(challenge_data['salt'])
cipher = StellarCipher(VAULT_KEY, engine)

@app.route('/api/v2/vault/status', methods=['GET'])
def get_status():
    return jsonify({
        "vault_id": "OO-STR-9921",
        "status": "LOCKED",
        "vault_salt": challenge_data['salt'],
        "blob": challenge_data['blob'],
        "integrity": "Custom-Rolling-v3",
        "note": "Packet: [IV(16)][CIPHERTEXT(N)][CHECKSUM(4)]"
    })

@app.route('/api/v2/vault/verify', methods=['POST'])
def verify_telemetry():
    # Subtle jitter
    time.sleep(random.uniform(0.005, 0.015))
    
    data = request.json
    if not data or 'blob' not in data:
        return jsonify({"error": "Missing telemetry blob"}), 400
    
    try:
        blob = bytes.fromhex(data['blob'])
        if len(blob) < 20:
            return jsonify({"error": "Packet too short"}), 400
        
        payload = blob[:-4]
        stored_checksum = struct.unpack(">I", blob[-4:])[0]
        
        # Custom integrity check
        if engine.compute_checksum(payload) != stored_checksum:
            return jsonify({"status": "error", "reason": "integrity_failure"}), 400

        iv = payload[:16]
        ct = payload[16:]
        
        # The Oracle logic
        # 0: Success, 1: Padding Error, 2: Schema Error
        trace_id = hashlib.md5(blob).hexdigest()
        result = cipher.verify_v3(iv, ct)
        
        if result == 0:
            return jsonify({"status": "success", "message": "Telemetry accepted", "trace": trace_id})
        
        # HARDENED SIDE-CHANNEL: JSON Key Ordering
        # Padding Error -> {"status": "error", "trace": "..."}
        # Schema Error -> {"trace": "...", "status": "error"}
        if result == 1:
            # Use a list of tuples to force order in older Python, or dict literals in 3.7+
            # Flask's jsonify preserves order by default in recent versions.
            response_data = {"status": "error", "trace": trace_id}
        else:
            response_data = {"trace": trace_id, "status": "error"}
            
        return make_response(jsonify(response_data), 400)
            
    except Exception:
        return jsonify({"error": "Internal processing error"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)