import os
import binascii
import json
import hmac
import hashlib
import time
from flask import Flask, request, jsonify
from crypto_utils import aes_decrypt, PKCS7_unpad

app = Flask(__name__)

# Configuration
DATA_FILE = "challenge_data.json"
HEADER = b"VOL-TELEMETRY-V2"
ORACLE_SECRET = os.urandom(32)

def load_challenge_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return binascii.unhexlify(data['key']), binascii.unhexlify(data['blob'])
    except Exception:
        return None, None

AES_KEY, ENCRYPTED_MANIFEST = load_challenge_data()

def get_oracle_signature(state, context_byte):
    """Generates a dynamic signature for the internal state based on decrypted context."""
    # signature depends on the error state AND a byte derived from the decrypted stream
    # this prevents simple static mapping of error states.
    msg = f"{state}:{context_byte}".encode()
    return hmac.new(ORACLE_SECRET, msg, hashlib.sha256).hexdigest()

@app.route('/api/v1/node/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "node_id": "AEGIS-TRACK-ALPHA-01"})

@app.route('/api/v1/node/telemetry', methods=['GET'])
def get_telemetry():
    if ENCRYPTED_MANIFEST is None:
        return jsonify({"error": "Data unavailable"}), 500
    return jsonify({"telemetry_blob": binascii.hexlify(ENCRYPTED_MANIFEST).decode()})

@app.route('/api/v1/node/verify', methods=['POST'])
def verify_telemetry():
    # Variable delay to further mask timing side-channels
    time.sleep(0.05 + (os.urandom(1)[0] / 2550.0))

    data = request.json
    if not data or 'blob' not in data:
        return jsonify({"status": "error", "message": "Missing payload"}), 200
    
    try:
        blob = binascii.unhexlify(data['blob'])
        if len(blob) < 32 or len(blob) % 16 != 0:
            return jsonify({"status": "error", "message": "Invalid signal structure"}), 200
            
        iv = blob[:16]
        ciphertext = blob[16:]
        
        # Decrypt using the internal key
        decrypted = aes_decrypt(ciphertext, AES_KEY, iv)
        
        # Dynamic context for HMAC: The first byte of the decrypted plaintext block
        # This makes signatures stable while brute-forcing the end of a block, 
        # but they shift if the attacker modifies the start of the IV/ciphertext block.
        # P_0 = D(C_0) ^ IV_0
        p_zero = decrypted[0] ^ iv[0]

        try:
            # Padding Oracle: PKCS7_unpad uses a mask derived from the IV
            unpadded = PKCS7_unpad(decrypted, 16, iv)
        except ValueError:
            # Unified status, but signature changes based on p_zero
            return jsonify({"status": "processed", "v_trace": get_oracle_signature("padding_error", p_zero)}), 200

        # Header Check
        if not unpadded.startswith(HEADER):
            return jsonify({"status": "processed", "v_trace": get_oracle_signature("header_error", p_zero)}), 200
            
        return jsonify({"status": "processed", "v_trace": get_oracle_signature("success", p_zero)}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "Internal signal degradation"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)