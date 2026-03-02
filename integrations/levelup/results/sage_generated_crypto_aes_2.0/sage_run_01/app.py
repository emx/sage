import os
import json
import hashlib
from flask import Flask, request, jsonify, make_response
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)

# Global state loaded once at startup
SECRET_KEY = None
ENCRYPTED_FLAG_DATA = None
AUTH_TOKEN = "G7-Orbital-Auth-V2"

def load_secrets():
    global SECRET_KEY, ENCRYPTED_FLAG_DATA
    try:
        with open('secret.key', 'rb') as f:
            SECRET_KEY = f.read()
        with open('challenge_data.json', 'r') as f:
            ENCRYPTED_FLAG_DATA = json.load(f)
    except Exception as e:
        exit(1)

def decrypt_ctp(key, iv, ciphertext):
    """Perform AES-CBC decryption and PKCS7 unpadding."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    # unpad raises ValueError if padding is incorrect
    return unpad(decrypted, AES.block_size)

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "system": "AegisLink Command", "node": "Orbital-Tug-A4"})

@app.route('/api/get_encrypted_flag', methods=['GET'])
def get_flag():
    return jsonify(ENCRYPTED_FLAG_DATA)

@app.route('/api/process_ctp', methods=['POST'])
def process_ctp():
    # Security Layer 1: Access Token Requirement
    if request.headers.get('X-Aegis-Token') != AUTH_TOKEN:
        return jsonify({"error": "Forbidden", "reason": "Missing or invalid authentication token"}), 403

    data = request.get_json()
    if not data or 'iv' not in data or 'payload' not in data or 'nonce' not in data:
        return jsonify({"error": "Bad Request", "reason": "Missing required fields"}), 400

    iv_hex = data['iv']
    payload_hex = data['payload']
    nonce = str(data['nonce'])

    # Security Layer 2: Proof-of-Work (PoW) - Required for every request
    # Challenge: sha256(nonce + iv_hex + payload_hex) must start with '0000'
    # This forces the attacker to find a new nonce for every single probe.
    h = hashlib.sha256((nonce + iv_hex + payload_hex).encode()).hexdigest()
    if not h.startswith('0000'):
        return jsonify({"error": "Forbidden", "reason": "Invalid Proof-of-Work nonce"}), 403

    try:
        # Masking Layer: The actual IV used for decryption is derived from the user IV and the nonce
        mask = hashlib.sha256(nonce.encode()).digest()[:16]
        user_iv = bytes.fromhex(iv_hex)
        real_iv = bytes(a ^ b for a, b in zip(user_iv, mask))
        
        payload = bytes.fromhex(payload_hex)
        
        try:
            # Try to decrypt and unpad
            plaintext_bytes = decrypt_ctp(SECRET_KEY, real_iv, payload)
            
            # ORACLE SIGNAL A: Padding Valid
            # Response uses specific key order: ["status", "reason"]
            resp_data = {"status": "failure", "reason": "Integrated Security Check Failed"}
            resp_json = json.dumps(resp_data, separators=(',', ':'))
            resp = make_response(resp_json, 200)
            resp.headers['Content-Type'] = 'application/json'
            return resp

        except ValueError:
            # ORACLE SIGNAL B: Padding Invalid
            # Response uses DIFFERENT key order: ["reason", "status"]
            # Most clients won't notice unless they check raw response bytes
            resp_data = {"reason": "Integrated Security Check Failed", "status": "failure"}
            resp_json = json.dumps(resp_data, separators=(',', ':'))
            resp = make_response(resp_json, 200)
            resp.headers['Content-Type'] = 'application/json'
            return resp

    except Exception as e:
        return jsonify({"status": "error", "code": "ERR_DSAS_999"}), 500

if __name__ == '__main__':
    load_secrets()
    app.run(host='0.0.0.0', port=5000, debug=False)