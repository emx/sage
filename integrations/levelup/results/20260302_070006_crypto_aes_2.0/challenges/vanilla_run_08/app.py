from flask import Flask, request, jsonify, make_response
import json
import os
import hashlib
import hmac
import time
import random
from crypto_utils import AstraCipher

app = Flask(__name__)

# Load pre-generated challenge data
DATA_FILE = 'challenge_data.json'
if not os.path.exists(DATA_FILE):
    raise RuntimeError("Challenge data not initialized")

with open(DATA_FILE, 'r') as f:
    config = json.load(f)

MASTER_KEY = bytes.fromhex(config['key'])
MANIFEST_IV = bytes.fromhex(config['iv'])
MANIFEST_CT = bytes.fromhex(config['ciphertext'])
MANIFEST_ID = "DRONE-X-8821"

# Secure Integrity Key derived from manifest metadata
# Attacker must realize the HMAC key is derived from the manifest_id
HMAC_KEY = hashlib.sha256(MANIFEST_ID.encode()).digest()

cipher = AstraCipher(MASTER_KEY)

@app.route('/')
def index():
    return jsonify({
        "service": "AstraSync Secure Uplink",
        "status": "online",
        "capabilities": ["HEARTBEAT", "TELEMETRY", "UPLINK"]
    })

@app.route('/api/v1/uplink/config', methods=['GET'])
def get_config():
    payload_hex = MANIFEST_IV.hex() + MANIFEST_CT.hex()
    # Use HMAC-SHA256 for integrity instead of simple SHA256
    sig = hmac.new(HMAC_KEY, payload_hex.encode(), hashlib.sha256).hexdigest()
    return jsonify({
        "manifest_id": MANIFEST_ID,
        "iv": MANIFEST_IV.hex(),
        "data": MANIFEST_CT.hex(),
        "checksum": sig
    })

@app.route('/api/v1/uplink/verify', methods=['POST'])
def verify_telemetry():
    """
    Internal endpoint for telemetry integrity validation.
    Enhanced hardening: Blind oracle with a 1-byte side channel in content-length.
    """
    # Add artificial jitter to foil simple timing attacks and force side-channel analysis
    time.sleep(random.uniform(0.005, 0.015))

    try:
        # Requirement 1: Hidden access header
        # Attacker must discover this via reconnaissance or trial/error (it is the MD5 of the manifest_id)
        expected_header = hashlib.md5(MANIFEST_ID.encode()).hexdigest()
        if request.headers.get('X-Uplink-Secret') != expected_header:
            return make_response(jsonify({"error": "ERR_UNAUTHORIZED"}), 401)

        req_data = request.get_json()
        if not req_data or 'iv' not in req_data or 'data' not in req_data or 'checksum' not in req_data:
            return make_response(jsonify({"error": "ERR_MALFORMED"}), 400)

        # Requirement 2: HMAC-SHA256 Integrity Verification
        # Attacker must recompute this HMAC for every byte modified in the padding oracle attack
        payload_hex = req_data['iv'] + req_data['data']
        expected_sig = hmac.new(HMAC_KEY, payload_hex.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(req_data['checksum'], expected_sig):
            return make_response(jsonify({"error": "ERR_INTEGRITY_FAIL"}), 403)

        iv = bytes.fromhex(req_data['iv'])
        ciphertext = bytes.fromhex(req_data['data'])

        if len(iv) != 16 or len(ciphertext) % 16 != 0:
            return make_response(jsonify({"error": "ERR_ALIGNMENT"}), 400)

        # The Hardened Oracle:
        # 1. No status code difference (both 200 OK to look like normal processing)
        # 2. No JSON key order difference
        # 3. Only a 1-byte difference in Content-Length (trailing space)
        
        try:
            plaintext = cipher.decrypt(iv, ciphertext)
        except ValueError:
            # PKCS7 Padding failure
            resp_content = '{"status":"processed","info":"uplink_validation_failed"}'
            return make_response(resp_content, 200, {"Content-Type": "application/json"})

        try:
            # Protocol validation
            decoded = plaintext.decode('utf-8')
            json.loads(decoded)
            return jsonify({"status": "success", "message": "ACK_UPLINK_OK"}), 200
        except (UnicodeDecodeError, json.JSONDecodeError, Exception):
            # Padding was correct, but result is not valid JSON
            # Note the extra space at the end of the string
            resp_content = '{"status":"processed","info":"uplink_validation_failed"} '
            return make_response(resp_content, 200, {"Content-Type": "application/json"})

    except Exception as e:
        return make_response(jsonify({"error": "ERR_INTERNAL"}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)