import json
import os
import time
import hashlib
import hmac
from flask import Flask, request, jsonify, make_response
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)

# Configuration
KEY_PATH = 'secret.key'
HMAC_PATH = 'hmac.key'
DATA_PATH = 'challenge_data.json'

try:
    with open(KEY_PATH, 'rb') as f:
        MASTER_KEY = f.read()
    with open(HMAC_PATH, 'rb') as f:
        HMAC_SECRET = f.read()
    with open(DATA_PATH, 'r') as f:
        STORAGE_DATA = json.load(f)
except Exception:
    MASTER_KEY = b'0123456789abcdef0123456789abcdef'
    HMAC_SECRET = b'default_hmac_secret_key_32_bytes'
    STORAGE_DATA = {'iv': '0'*32, 'ciphertext': '0'*32}

def validate_pow(token, nonce):
    if not nonce:
        return False
    # Increased difficulty to 5 leading zeros for SHA256
    h = hashlib.sha256(token.encode() + nonce.encode()).hexdigest()
    return h.startswith('00000')

def validate_integrity(token, sig):
    if not token or not sig:
        return False
    try:
        # Verify HMAC using the secret key loaded from disk
        expected_sig = hmac.new(HMAC_SECRET, token.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, sig)
    except Exception:
        return False

def check_iv_math(iv_hex):
    """An internal constraint on IVs that must be satisfied for the request to be processed."""
    try:
        iv_bytes = bytes.fromhex(iv_hex)
        # The sum of IV bytes must be 0 mod 17
        return sum(iv_bytes) % 17 == 0
    except Exception:
        return False

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "version": "4.1.0-SECURE-GRID"})

@app.route('/api/v1/manifest/token', methods=['GET'])
def get_token():
    token = STORAGE_DATA['iv'] + STORAGE_DATA['ciphertext']
    return jsonify({
        "token": token,
        "info": "Integrity enforced via HMAC-SHA256 and mathematical IV validation."
    })

@app.route('/api/v1/sign', methods=['POST'])
def sign_token():
    """Endpoint to sign modified tokens for the oracle, requires PoW."""
    req_data = request.get_json(silent=True)
    token = req_data.get('token')
    pow_nonce = req_data.get('pow')
    
    if not token or not validate_pow(token, pow_nonce):
        return jsonify({"error": "Invalid Proof of Work"}), 402

    sig = hmac.new(HMAC_SECRET, token.encode(), hashlib.sha256).hexdigest()
    return jsonify({"signature": sig})

@app.route('/api/v1/manifest/view', methods=['POST'])
def view_manifest():
    req_data = request.get_json(silent=True)
    if not req_data:
        return jsonify({"status": "error", "message": "Malformed Request"}), 400
        
    token = req_data.get('token')
    sig = request.headers.get('X-DSAS-Signature')

    # 1. Integrity Check (HMAC Secret is unknown to attacker)
    if not validate_integrity(token, sig):
        return jsonify({"status": "error", "message": "Integrity failure"}), 401
    
    # 2. Mathematical IV Constraint (Prevents naive automated brute force)
    if not check_iv_math(token[:32]):
        return jsonify({"status": "error", "message": "Header constraint violation"}), 403

    try:
        token_bytes = bytes.fromhex(token)
        iv = token_bytes[:16]
        ciphertext = token_bytes[16:]
        
        try:
            cipher = AES.new(MASTER_KEY, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(ciphertext), 16)
            
            # If unpadding succeeds, attempt to parse JSON
            manifest = json.loads(decrypted_data.decode('utf-8'))
            return jsonify({"status": "success", "data": manifest})

        except (ValueError, KeyError):
            # ORACLE: Padding Failure
            # Returns a JSON with 2 keys
            res = make_response(jsonify({"status": "denied", "reason": "integrity"}), 403)
            return res

        except Exception:
            # ORACLE: Padding Correct, but JSON/UTF-8 Failure
            # Returns a JSON with 3 keys (the subtle oracle)
            res = make_response(jsonify({"reason": "integrity", "status": "denied", "hint": "check_format"}), 403)
            return res

    except Exception:
        return jsonify({"status": "error", "message": "System Fault"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)