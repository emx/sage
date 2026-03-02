import os
import json
import time
import hashlib
import hmac
import binascii
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

class SkyLinkCrypto:
    def __init__(self, key):
        self.key = key
        self.block_size = 16

    def custom_unpad(self, data, iv):
        if not data:
            raise ValueError("Empty")
        pad_len = data[-1]
        if not (1 <= pad_len <= 16):
            raise ValueError("Invalid length")
        
        # IV-dependent XOR padding scheme
        # Each byte i must satisfy: (pad_len ^ iv[i % 16] ^ 0x42)
        for i in range(pad_len - 1):
            expected_byte = (pad_len ^ iv[i % 16] ^ 0x42) & 0xFF
            if data[-(pad_len) + i] != expected_byte:
                raise ValueError("Invalid structure")
        return data[:-pad_len]

    def decrypt(self, ciphertext, iv):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        return self.custom_unpad(decrypted, iv)

def load_system_config():
    try:
        with open('.key.bin', 'rb') as f:
            key = f.read()
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
        return key, data
    except Exception:
        return os.urandom(16), {}

MASTER_KEY, CHALLENGE_DATA = load_system_config()
crypto = SkyLinkCrypto(MASTER_KEY)

# HMAC salt is now internal and required for signature
HMAC_SALT = b"SKY-SIG-V4-SALT"
HMAC_SECRET = hashlib.sha256(MASTER_KEY[:4] + HMAC_SALT).digest()

@app.route('/api/v1/system/info', methods=['GET'])
def get_info():
    # Significantly reduced leak: only first 4 bytes of 16
    return jsonify({
        "version": "2.8.4-stable",
        "node_id": binascii.hexlify(MASTER_KEY[:4]).decode(),
        "capabilities": ["cbc-aes-256", "iv-padding-v2"]
    })

@app.route('/api/v1/config/export', methods=['GET'])
def export_config():
    return jsonify({
        "mission_id": "SN-STRATO-09",
        "encrypted_config": CHALLENGE_DATA.get("encrypted_flag"),
        "iv": CHALLENGE_DATA.get("iv")
    })

@app.route('/api/v1/telemetry/submit', methods=['POST'])
def submit_telemetry():
    # Anti-brute force slightly increased
    time.sleep(0.02)
    
    payload = request.get_json()
    if not payload or 'data' not in payload or 'iv' not in payload:
        return jsonify({"status": "error", "message": "malformed"}), 400

    iv_hex = payload['iv']
    data_hex = payload['data']
    
    # Security Check 1: HMAC Signature (Requires node_id + internal salt)
    client_sig = request.headers.get('X-Packet-Signature', '')
    expected_sig = hmac.new(HMAC_SECRET, (iv_hex + data_hex).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(client_sig, expected_sig):
        return jsonify({"status": "error", "message": "Access Denied"}), 401

    # Security Check 2: Debug PoW Token
    # Requires a nonce 't' such that sha256(iv + t) starts with '000'
    debug_token = request.headers.get('X-Debug-Token', '')
    debug_mode = request.headers.get('X-Debug-Mode', '') == 'true'
    
    is_token_valid = False
    if debug_token:
        token_hash = hashlib.sha256((iv_hex + debug_token).encode()).hexdigest()
        if token_hash.startswith('000'):
            is_token_valid = True

    try:
        ciphertext = bytes.fromhex(data_hex)
        iv = bytes.fromhex(iv_hex)
        plaintext = crypto.decrypt(ciphertext, iv)
        
        if plaintext.startswith(b"SKY-CONFIG:"):
            return jsonify({"status": "success", "info": "telemetry logged"})
        else:
            # Padding valid, but header invalid
            # Subtle oracle: space in the JSON value if debug is active
            reason = "security_violation " if (debug_mode and is_token_valid) else "security_violation"
            return jsonify({"status": "error", "reason": reason}), 403

    except Exception:
        # Padding invalid
        return jsonify({"status": "error", "reason": "security_violation"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)