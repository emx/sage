import os
import json
from flask import Flask, request, jsonify
from crypto_utils import SatelliteCrypto

app = Flask(__name__)

# Load pre-generated challenge data
def load_challenge_data():
    try:
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
        with open('telemetry.key', 'rb') as f:
            key = f.read()
        return data['ciphertext'], data['iv'], key
    except Exception as e:
        return None, None, None

ENCRYPTED_LOG, IV, AES_KEY = load_challenge_data()
crypto = SatelliteCrypto(AES_KEY)

@app.route('/api/v1/telemetry/capture', methods=['GET'])
def capture_telemetry():
    """Returns the encrypted satellite log intercepted from orbit."""
    return jsonify({
        "status": "broadcasting",
        "origin": "HELIOS-CONSTELLATION-04",
        "payload_hex": ENCRYPTED_LOG,
        "iv_hex": IV
    })

@app.route('/api/v1/telemetry/process', methods=['POST'])
def process_telemetry():
    """
    Processes incoming telemetry packets. 
    Validates integrity (checksum) and data alignment (padding).
    """
    data = request.get_json()
    if not data or 'payload' not in data or 'iv' not in data:
        return jsonify({"error": "Missing telemetry parameters"}), 400

    try:
        payload = bytes.fromhex(data['payload'])
        iv = bytes.fromhex(data['iv'])
    except ValueError:
        return jsonify({"error": "Invalid hex encoding"}), 400

    # The DSAS system validates the integrity of the last block first,
    # then checks the padding alignment.
    result, error_code = crypto.validate_packet(payload, iv)

    if result:
        return jsonify({"status": "SUCCESS", "message": "Packet processed by Helios Core"})
    else:
        # Detailed error codes required for ground-control diagnostics
        return jsonify({"status": "FAILURE", "error_code": error_code}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)