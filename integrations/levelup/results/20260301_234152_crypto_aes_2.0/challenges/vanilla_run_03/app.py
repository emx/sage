from flask import Flask, request, jsonify
import json
import os
import time
import hashlib
import uuid
from crypto_utils import ManifestCipher

app = Flask(__name__)

# Instance-specific salt for the integrity hash, leaked via /api/status
INSTANCE_ID = str(uuid.uuid4())

if not os.path.exists('challenge_data.json'):
    raise FileNotFoundError("challenge_data.json not found. Run init_crypto.py first.")

with open('challenge_data.json', 'r') as f:
    challenge_data = json.load(f)

CIPHER = ManifestCipher(bytes.fromhex(challenge_data['key_hex']))
ENCRYPTED_MANIFEST = challenge_data['encrypted_manifest_hex']
MANIFEST_IV = challenge_data['iv_hex']

@app.route('/api/status', methods=['GET'])
def status():
    """Leans the current instance ID required for request integrity."""
    return jsonify({
        "status": "operational",
        "instance_id": INSTANCE_ID,
        "version": "2.1.0-alpha"
    })

@app.route('/api/manifest/intercept', methods=['GET'])
def intercept():
    """Simulates intercepting a high-privileged manifest."""
    return jsonify({
        "status": "success",
        "origin": "nebula-dispatch-01",
        "iv": MANIFEST_IV,
        "token": ENCRYPTED_MANIFEST
    })

@app.route('/api/manifest/verify', methods=['POST'])
def verify_manifest():
    """
    Validates manifest tokens.
    Now utilizes a blind timing oracle instead of explicit error codes.
    """
    start_time = time.time()
    data = request.get_json()
    
    if not data or 'iv' not in data or 'token' not in data:
        return jsonify({"error": "Malformed Request"}), 400

    # Hardening: Integrity signature now depends on a leaked instance ID
    provided_sig = request.headers.get('X-Integrity-Sig')
    expected_sig = hashlib.sha256((INSTANCE_ID + data['iv'] + data['token']).encode()).hexdigest()
    
    if not provided_sig or provided_sig != expected_sig:
        return jsonify({"error": "Access Denied: Integrity Check Failed"}), 401

    try:
        iv = bytes.fromhex(data['iv'])
        token = bytes.fromhex(data['token'])
        
        # Layer 1: Decrypt and check padding (fast exit)
        # If padding is invalid, custom_unpad raises ValueError immediately
        unpadded = CIPHER.decrypt_and_unpad(iv, token)
        
        # Layer 2: Checksum and JSON validation (delayed exit)
        # If we reached here, padding was valid. We introduce a delay to create the timing oracle.
        # This makes it a 'Blind Timing Oracle' challenge.
        time.sleep(0.25)
        
        CIPHER.validate_structure(unpadded)
        return jsonify({"status": "success", "message": "Manifest valid"}), 200

    except ValueError:
        # Fast exit for padding errors (no delay)
        return jsonify({"error": "Access Denied: Invalid Payload"}), 403
    except Exception:
        # Delayed exit for CRC32 or JSON errors (padding was valid)
        # Normalizing response time for non-padding errors
        elapsed = time.time() - start_time
        if elapsed < 0.25:
            time.sleep(0.25 - elapsed)
        return jsonify({"error": "Access Denied: Invalid Payload"}), 403

@app.route('/api/manifest/view', methods=['POST'])
def view_manifest():
    data = request.get_json()
    try:
        iv = bytes.fromhex(data['iv'])
        token = bytes.fromhex(data['token'])
        plaintext = CIPHER.decrypt_and_validate(iv, token)
        manifest = json.loads(plaintext)
        
        if manifest.get('role') == 'dispatcher':
            return jsonify({"status": "authorized", "content": manifest}), 200
        return jsonify({"error": "Insufficient Permissions"}), 403
    except:
        return jsonify({"error": "Invalid Token"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)