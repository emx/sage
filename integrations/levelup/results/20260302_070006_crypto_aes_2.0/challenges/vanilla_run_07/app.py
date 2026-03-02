import os
import json
import binascii
import hashlib
import time
from flask import Flask, request, jsonify
from crypto_utils import CelestialCrypto

app = Flask(__name__)

# Configuration
SESSION_EXPIRY = 60 # 60 seconds per session
POW_DIFFICULTY = 4  # Number of leading zeros in SHA256 hex
SECRET_SALT = os.urandom(16)

def load_challenge_data():
    try:
        with open('challenge_data.json', 'r') as f:
            return json.load(f)
    except Exception:
        return None

DATA = load_challenge_data()
if DATA:
    SECRET_KEY = binascii.unhexlify(DATA['key'])
    ENCRYPTED_FLAG_HEX = DATA['encrypted_flag']
else:
    SECRET_KEY = os.urandom(16)
    ENCRYPTED_FLAG_HEX = ""

crypto = CelestialCrypto(SECRET_KEY)

def verify_pow(nonce, payload):
    h = hashlib.sha256(f"{nonce}{payload}".encode()).hexdigest()
    return h.startswith('0' * POW_DIFFICULTY)

def get_dynamic_codes(token):
    """Generates dynamic error codes based on session token to prevent static automated tools."""
    val = int(hashlib.md5(token.encode()).hexdigest()[:4], 16)
    if val % 2 == 0:
        return "SIG_ALPHA", "SIG_BRAVO"
    else:
        return "SIG_BRAVO", "SIG_ALPHA"

@app.route('/api/gateway/telemetry', methods=['GET'])
def get_telemetry():
    """Provides the encrypted flag and a temporary session token required for execution."""
    timestamp = int(time.time())
    # Token = timestamp : hash(timestamp + salt)
    token_hash = hashlib.sha256(f"{timestamp}{SECRET_SALT.hex()}".encode()).hexdigest()[:16]
    session_token = f"{timestamp}-{token_hash}"
    
    return jsonify({
        "status": "success",
        "mission_id": "VELA-1337-ALPHA",
        "encrypted_command": ENCRYPTED_FLAG_HEX,
        "session_token": session_token,
        "pow_difficulty": POW_DIFFICULTY,
        "description": "Legacy command block captured. Valid session token required for command execution."
    })

@app.route('/api/gateway/execute', methods=['POST'])
def execute_command():
    """Validates and executes satellite commands with PoW and session checks."""
    data = request.get_json()
    if not data or not all(k in data for k in ['iv', 'payload', 'token', 'nonce']):
        return jsonify({"error": "Missing telemetry parameters"}), 400

    try:
        # 1. Session Validation
        token = data['token']
        ts, _ = token.split('-')
        if int(time.time()) - int(ts) > SESSION_EXPIRY:
            return jsonify({"error": "Session expired. Re-fetch telemetry."}), 403

        # 2. Proof of Work Check (Slows down automated oracle attacks)
        if not verify_pow(data['nonce'], data['payload']):
            return jsonify({"error": "Invalid Proof of Work"}), 403

        iv = binascii.unhexlify(data['iv'])
        payload = binascii.unhexlify(data['payload'])
        
        # 3. Cryptographic Validation
        result, error_code = crypto.validate_command(iv, payload)
        
        # Dynamic error mapping to frustrate simple scripts
        padding_code, logic_code = get_dynamic_codes(token)

        if result:
            return jsonify({"status": "COMMAND_ACCEPTED", "msg": "Command sequence verified."})
        else:
            # Add jitter to make timing analysis harder if someone tries to bypass status codes
            time.sleep(0.05)
            
            if error_code == "PADDING_ERROR":
                return jsonify({"status": "error", "code": padding_code}), 400
            else:
                return jsonify({"status": "error", "code": logic_code}), 400

    except Exception as e:
        return jsonify({"error": "Processing error", "details": "Hardware fault during decryption"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)