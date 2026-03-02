import os
import json
import hashlib
from flask import Flask, request, jsonify, abort
from crypto_utils import AESCipher, PaddingError

app = Flask(__name__)

# Diagnostic key for oracle responses - intended to be found via source analysis
DIAGNOSTIC_KEY = b"AETHER_DIAG_9971"

# Load the secret key and system token generated during build
try:
    with open('challenge_data.json', 'r') as f:
        challenge_data = json.load(f)
        ENCRYPTED_SYSTEM_BLOB = challenge_data['encrypted_system_blob']
        SERVICE_KEY = bytes.fromhex(challenge_data['service_key'])
        FLAG = challenge_data['flag']
except Exception:
    SERVICE_KEY = os.urandom(16)
    ENCRYPTED_SYSTEM_BLOB = ""
    FLAG = "LEVELUP{DEBUG_FLAG}"

cipher = AESCipher(SERVICE_KEY)
diag_cipher = AESCipher(DIAGNOSTIC_KEY)

def verify_pow(nonce):
    if not nonce:
        return False
    # Requires a simple SHA256 prefix collision (4 leading zeros) to throttle automated oracle attempts
    h = hashlib.sha256(nonce.encode()).hexdigest()
    return h.startswith("0000")

@app.route('/api/v1/info', methods=['GET'])
def info():
    guest_manifest = {"role": "guest", "id": "GEN-402", "ts": "2023-11-15"}
    encrypted_guest = cipher.encrypt(json.dumps(guest_manifest))
    return jsonify({
        "description": "Aetherius Secure Management Node v3.0 (Hardened)",
        "manifest_template": encrypted_guest,
        "restricted_system_blob": ENCRYPTED_SYSTEM_BLOB,
        "diagnostic_key": DIAGNOSTIC_KEY.decode(),
        "note": "PoW required for verification. Hash(nonce) must start with '0000'."
    })

@app.route('/api/v1/verify', methods=['POST'])
def verify():
    req_data = request.json
    if not req_data or 'manifest' not in req_data or 'pow' not in req_data:
        return jsonify({"error": "Missing manifest or PoW nonce"}), 400
    
    if not verify_pow(req_data['pow']):
        return jsonify({"error": "Invalid Proof-of-Work"}), 403

    manifest_hex = req_data['manifest']
    result = {"valid": False, "code": "ERR_UNKNOWN"}
    
    try:
        # The Padding Oracle is now blinded behind an encrypted response
        plaintext = cipher.decrypt(manifest_hex)
        try:
            json.loads(plaintext.decode())
            result = {"valid": True, "code": "SUCCESS"}
        except Exception:
            result = {"valid": False, "code": "ERR_INTEGRITY"}
    except PaddingError:
        result = {"valid": False, "code": "ERR_PADDING"}
    except Exception:
        result = {"valid": False, "code": "ERR_FATAL"}

    # Always return 200 OK, but with an encrypted diagnostic report
    report = diag_cipher.encrypt(json.dumps(result))
    return jsonify({"report": report})

@app.route('/api/v1/process', methods=['POST'])
def process():
    req_data = request.json
    if not req_data or 'manifest' not in req_data:
        return jsonify({"error": "Missing manifest"}), 400

    try:
        plaintext = cipher.decrypt(req_data['manifest'])
        manifest = json.loads(plaintext.decode())
        
        system_data = json.loads(cipher.decrypt(ENCRYPTED_SYSTEM_BLOB).decode())
        required_token = system_data.get('system_token')

        if manifest.get('role') == 'admin' and manifest.get('token') == required_token:
            return jsonify({"status": "authorized", "flag": FLAG})
        else:
            return jsonify({"status": "unauthorized", "message": "Administrative privileges required."}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": "Process execution failed."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)