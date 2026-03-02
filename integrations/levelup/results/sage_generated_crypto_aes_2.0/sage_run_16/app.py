import os
import json
import hashlib
import secrets
import time
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Custom Padding: PKCS7-style but XORed with 0x42
def custom_unpad(padded_data, block_size=16):
    if len(padded_data) % block_size != 0 or len(padded_data) == 0:
        raise ValueError("Invalid block alignment")
    last_byte = padded_data[-1]
    pad_len = last_byte ^ 0x42
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid padding length")
    for i in range(1, pad_len + 1):
        if (padded_data[-i] ^ 0x42) != pad_len:
            raise ValueError("Invalid padding bytes")
    return padded_data[:-pad_len]

# Load pre-generated challenge data
with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

KEY = bytes.fromhex(CHALLENGE_DATA['secret_key_hex'])
FLAG_TOKEN = CHALLENGE_DATA['encrypted_dispatch']

def aes_decrypt_oracle(token_hex, key):
    try:
        data = bytes.fromhex(token_hex)
        if len(data) < 32:
            return False, "ERR_AUTH_FAILURE"
            
        iv = data[:16]
        ciphertext = data[16:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        
        # Padding Oracle Point with Side-Channel Timing
        try:
            decrypted = custom_unpad(decrypted_padded, 16)
            # If padding is valid, we perform a compute-heavy operation to create a timing differential
            # This makes the oracle blind (no explicit error codes) but detectable via timing.
            hashlib.pbkdf2_hmac('sha256', decrypted, b'chrono_salt_v2', 80000)
        except ValueError:
            # Invalid padding returns immediately
            return False, "ERR_AUTH_FAILURE"
            
        # Structural Check
        if not decrypted.startswith(b"CHRONO|"):
            return False, "ERR_AUTH_FAILURE"
            
        return True, "SUCCESS"
    except Exception:
        return False, "ERR_AUTH_FAILURE"

@app.before_request
def check_pow():
    if request.path == '/api/v1/dispatch/flag_token' or request.path == '/api/v1/pow_challenge':
        return
    
    if request.method == 'POST':
        data = request.get_json() or {}
        salt = data.get('pow_salt')
        nonce = data.get('pow_nonce')
        
        if not salt or not nonce:
            return jsonify({"error": "Proof of Work required", "pow_difficulty": 4}), 400
        
        h = hashlib.sha256((str(salt) + str(nonce)).encode()).hexdigest()
        # Difficulty increased slightly to 18 bits (4 leading zeros and first digit < 4)
        if not (h.startswith('0000') and int(h[4], 16) < 4):
            return jsonify({"error": "Invalid Proof of Work"}), 403

@app.route('/api/v1/dispatch/flag_token', methods=['GET'])
def get_flag_token():
    return jsonify({
        "description": "ChronoLink Secure Dispatch Manifest v2.1",
        "token": FLAG_TOKEN,
        "pow_hint": "SHA256(salt + nonce) must start with '0000' and 5th char < 4 (18-bit difficulty)"
    })

@app.route('/api/v1/dispatch/validate', methods=['POST'])
def validate_token():
    data = request.get_json()
    token_hex = data.get('token')
    
    if not token_hex:
        return jsonify({"error": "Missing token"}), 400

    # The oracle is now blind; success and failure look identical in content
    success, code = aes_decrypt_oracle(token_hex, KEY)
    if success:
        return jsonify({"status": "success", "message": "Dispatch verified"})
    else:
        return jsonify({"status": "error", "code": "ERR_AUTH_FAILURE"}), 200

@app.route('/api/v1/pow_challenge', methods=['GET'])
def get_pow():
    salt = secrets.token_hex(8)
    return jsonify({"pow_salt": salt, "pow_difficulty": "18-bit"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)