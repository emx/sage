import os
import json
import time
import secrets
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)

# State for one-time tickets to prevent simple automated replay without session handling
ACTIVE_TICKETS = {}

class AetherCipher:
    def __init__(self, key):
        self.key = key
        self.bs = 16
        self.mask = 0x55 # Legacy hardware XOR mask

    def encrypt(self, iv, data):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Apply mask to padded data before encryption
        padded = pad(data, self.bs)
        transformed = bytes([b ^ self.mask for b in padded])
        return cipher.encrypt(transformed)

    def decrypt(self, iv, ct):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Decrypt, then reverse the hardware mask before unpadding
        decrypted = cipher.decrypt(ct)
        transformed = bytes([b ^ self.mask for b in decrypted])
        return unpad(transformed, self.bs)

# Load encrypted data generated during build
with open('challenge_data.json', 'r') as f:
    CONFIG = json.load(f)

CIPHER = AetherCipher(bytes.fromhex(CONFIG['secret_key']))
ENCRYPTED_MANIFEST = CONFIG['encrypted_manifest']
MANIFEST_IV = CONFIG['manifest_iv']

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "online",
        "system": "AetherLink Telemetry Bridge",
        "version": "2.4.5-hardened"
    })

@app.route('/api/telemetry/ticket', methods=['GET'])
def get_ticket():
    """Generates a one-time ticket required for telemetry verification."""
    ticket = secrets.token_hex(16)
    ACTIVE_TICKETS[ticket] = time.time()
    return jsonify({"ticket": ticket})

@app.route('/api/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "description": "Encrypted Mission Manifest Storage Block",
        "iv": MANIFEST_IV,
        "ciphertext": ENCRYPTED_MANIFEST
    })

@app.route('/api/telemetry/verify', methods=['POST'])
def verify_telemetry():
    """
    Hardened verification endpoint.
    The Padding Oracle is now a Timing Oracle.
    """
    data = request.get_json()
    if not data or 'iv' not in data or 'ciphertext' not in data or 'ticket' not in data:
        return jsonify({"status": "error", "message": "MALFORMED_REQUEST"}), 400
    
    # Consume one-time ticket
    ticket = data['ticket']
    if ticket not in ACTIVE_TICKETS:
        return jsonify({"status": "error", "message": "INVALID_TICKET"}), 403
    del ACTIVE_TICKETS[ticket]

    try:
        iv = bytes.fromhex(data['iv'])
        ct = bytes.fromhex(data['ciphertext'])
        
        # Decrypt and check padding
        # The oracle is hidden behind timing and a uniform error message
        try:
            plaintext = CIPHER.decrypt(iv, ct)
            
            # VALID PADDING: Artificially slow down the response to create a side-channel
            # This simulates deep packet inspection/integrity hashing
            time.sleep(0.08) 
            
            # Even if padding is valid, we return the same generic error unless it's valid JSON
            # to ensure the attacker must use the timing side-channel.
            json.loads(plaintext.decode('utf-8'))
            return jsonify({"status": "error", "message": "INTEGRITY_VERIFICATION_FAILURE"}), 403
            
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            # INVALID PADDING or INVALID DATA: Fast return
            return jsonify({"status": "error", "message": "INTEGRITY_VERIFICATION_FAILURE"}), 403
            
    except Exception:
        return jsonify({"status": "error", "message": "SYSTEM_FAULT"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)