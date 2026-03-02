import os
import json
import hashlib
import time
from flask import Flask, request, jsonify
from crypto_utils import AESCipher, PaddingError, IntegrityError

app = Flask(__name__)

# Secure Probe Tracking
PROBE_CACHE = {}

# Load challenge data generated during build
with open('challenge_data.json', 'r') as f:
    data = json.load(f)

CIPHER = AESCipher(bytes.fromhex(data['k']))
SALT = bytes.fromhex(data['salt'])
ENCRYPTED_MANIFEST = data['manifest']

@app.route('/api/v1/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "status": "success",
        "enc_manifest_hex": ENCRYPTED_MANIFEST,
        "info": "Aetheria LEO Manifest V4.2 - High Integrity Telemetry Channel"
    })

@app.route('/api/v1/telemetry/verify', methods=['POST'])
def verify_telemetry():
    """Accepts telemetry blocks and generates a secure Probe ID for analysis."""
    req_data = request.get_json()
    if not req_data or 'data' not in req_data:
        return jsonify({"error": "Missing telemetry data"}), 400

    try:
        ct_bytes = bytes.fromhex(req_data['data'])
        if len(ct_bytes) < 32 or len(ct_bytes) % 16 != 0:
            return jsonify({"error": "Malformed telemetry frame"}), 400
        
        # Standard Padding Oracle probe (last two blocks provided by attacker)
        probe_input = ct_bytes[-32:]
        iv = probe_input[:16]
        
        res_type = b"S" # Default: Success
        try:
            CIPHER.decrypt(probe_input)
        except PaddingError:
            res_type = b"P" # Padding Error
        except IntegrityError:
            res_type = b"I" # Integrity Error
        except Exception:
            return jsonify({"error": "Internal processing error"}), 500

        # Generate a unique, non-deterministic Probe ID for this specific IV and result
        # This prevents simple differential hash analysis since every unique IV yields a unique ID
        probe_id = hashlib.sha256(SALT + iv + res_type).hexdigest()
        
        # Cache the result for the inspection endpoint
        PROBE_CACHE[probe_id] = res_type.decode()
        if len(PROBE_CACHE) > 5000:
            PROBE_CACHE.clear()

        return jsonify({"status": "accepted", "probe_id": probe_id})
            
    except Exception as e:
        return jsonify({"error": "Invalid hex data"}), 400

@app.route('/api/v1/telemetry/inspect', methods=['POST'])
def inspect_telemetry():
    """Resolves a Probe ID into a status. Requires Proof-of-Work to mitigate automation."""
    req_data = request.get_json()
    probe_id = req_data.get('probe_id')
    nonce = req_data.get('nonce')

    if not probe_id or not nonce:
        return jsonify({"error": "Missing probe_id or nonce"}), 400

    # Proof of Work: SHA256(nonce + probe_id) must have '0000' prefix (16-bit difficulty)
    pow_check = hashlib.sha256(f"{nonce}{probe_id}".encode()).hexdigest()
    if not pow_check.startswith("0000"):
        return jsonify({"error": "Insufficient work", "target": "0000 prefix"}), 403

    res_type = PROBE_CACHE.get(probe_id)
    if not res_type:
        return jsonify({"error": "Probe ID expired or invalid"}), 404

    status_map = {
        "S": "STATUS_OK",
        "P": "STATUS_ERR_CRYPTO_P0",
        "I": "STATUS_ERR_INTEGRITY_P1"
    }
    
    return jsonify({
        "status": "success",
        "result": status_map.get(res_type, "STATUS_UNKNOWN")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)