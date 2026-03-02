import os
import json
import hashlib
import time
from flask import Flask, request, jsonify
from crypto_utils import AstraSyncCipher

app = Flask(__name__)

INTERNAL_DATA_PATH = "challenge_data.json"
KEY_PATH = "key.bin"
MAGIC_HEADER = b"ASTRA_V2:"

try:
    with open(KEY_PATH, "rb") as f:
        AES_KEY = f.read()
except FileNotFoundError:
    AES_KEY = os.urandom(16)

cipher_suite = AstraSyncCipher(AES_KEY)

try:
    with open(INTERNAL_DATA_PATH, "r") as f:
        manifest_data = json.load(f)
        ENCRYPTED_FLAG_MANIFEST = manifest_data["manifest"]
except FileNotFoundError:
    ENCRYPTED_FLAG_MANIFEST = ""

def verify_pow(nonce, payload):
    check = hashlib.sha256(f"{nonce}{payload}".encode()).hexdigest()
    return check.startswith("00000")

@app.route('/api/v1/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "status": "success",
        "manifest_id": "VOL-ASTRA-99",
        "payload_hex": ENCRYPTED_FLAG_MANIFEST,
        "pow_difficulty": 5
    })

@app.route('/api/v1/validate', methods=['POST'])
def validate_manifest():
    data = request.get_json()
    if not data or 'payload' not in data or 'nonce' not in data:
        return jsonify({"status": "error", "code": "0x80041005"}), 400

    if not verify_pow(data['nonce'], data['payload']):
        return jsonify({"status": "error", "code": "0x80041003"}), 403

    try:
        payload = bytes.fromhex(data['payload'])
        if len(payload) < 32 or len(payload) % 16 != 0:
            return jsonify({"status": "error", "code": "0x80041001"}), 200
        
        iv = payload[:16]
        ciphertext = payload[16:]
        
        # Decryption attempt
        decrypted_pt = cipher_suite.decrypt(iv, ciphertext)
        
        if decrypted_pt is None:
            # Return identical error immediately on padding failure
            return jsonify({"status": "error", "code": "0x80041001"}), 200
        
        # Valid padding detected - trigger timing side-channel
        # This makes it a Timing Oracle rather than a Response-Body Oracle
        time.sleep(0.05)
        
        if not decrypted_pt.startswith(MAGIC_HEADER):
            return jsonify({"status": "error", "code": "0x80041001"}), 200

        try:
            json_content = json.loads(decrypted_pt[len(MAGIC_HEADER):].decode('utf-8'))
            return jsonify({
                "status": "success",
                "code": "0x00000000",
                "ref": hashlib.md5(json_content.get("manifest_id", "").encode()).hexdigest()[:8]
            }), 200
        except Exception:
            return jsonify({"status": "error", "code": "0x80041001"}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "code": "0x80045000"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)