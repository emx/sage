import os
import json
import hashlib
from flask import Flask, request, jsonify
from crypto_utils import AESCipher, POWManager

app = Flask(__name__)
app.json.sort_keys = False

# Secure configuration loading
with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

CIPHER = AESCipher(bytes.fromhex(CHALLENGE_DATA['key']))
# PoW difficulty increased to further throttle oracle attempts
POW = POWManager(difficulty=6)

@app.route('/telemetry/config', methods=['GET'])
def get_config():
    return jsonify({
        "mission": "Stratus-4",
        "encrypted_blob": CHALLENGE_DATA['encrypted_config'],
        "version": "3.1.0-alpha"
    })

@app.route('/telemetry/pow_challenge', methods=['GET'])
def get_pow():
    prefix = POW.generate_challenge()
    return jsonify({"prefix": prefix, "difficulty": 6, "algorithm": "sha256"})

def generate_trace(success):
    """Generates a trace ID where the parity of the last digit leaks status."""
    base = hashlib.sha256(os.urandom(16)).hexdigest()[:-1]
    # If success (padding ok), last digit is even (0). If fail, last digit is odd (1).
    return base + ('0' if success else '1')

@app.route('/telemetry/verify', methods=['POST'])
def verify_command():
    req_data = request.get_json()
    if not req_data or not all(k in req_data for k in ('packet', 'pow', 'prefix')):
        return jsonify({"status": "error", "code": "E-000"}), 400

    if not POW.verify(req_data['prefix'], req_data['pow']):
        return jsonify({"status": "error", "code": "E-001"}), 403

    try:
        ciphertext = bytes.fromhex(req_data['packet'])
        if len(ciphertext) < 32 or len(ciphertext) % 16 != 0:
            return jsonify({"status": "error", "code": "E-002"}), 400

        # Decrypt using modified bit-shifted CBC
        pt_padded = CIPHER.raw_decrypt(ciphertext)
        
        # Step 1: Padding Validation (ISO/IEC 7816-4)
        plaintext = CIPHER.unpad_protocol(pt_padded)
        
        # The oracle is now 'blind'. We return the same error code but different trace parities.
        if plaintext is None:
            # Padding Failure: Trace ends in '1'
            return jsonify({"status": "error", "code": "E-1029", "trace": generate_trace(False)}), 200

        # Step 2: Protocol Header Validation
        if not plaintext.startswith(b"SYS"):
            # Header Failure (Padding was OK): Trace ends in '0'
            return jsonify({"status": "error", "code": "E-1029", "trace": generate_trace(True)}), 200

        # Step 3: Application Data Parsing
        try:
            json_data = json.loads(plaintext[3:].decode('utf-8'))
            if "cmd" in json_data:
                return jsonify({"status": "success", "msg": "COMMAND_ACCEPTED"}), 200
            else:
                return jsonify({"status": "error", "code": "E-2041", "trace": generate_trace(True)}), 200
        except:
            return jsonify({"status": "error", "code": "E-3099", "trace": generate_trace(True)}), 200

    except Exception as e:
        return jsonify({"status": "error", "code": "E-999"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)