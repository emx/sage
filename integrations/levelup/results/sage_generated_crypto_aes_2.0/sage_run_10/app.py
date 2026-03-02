import os
import json
import secrets
import time
import hashlib
from flask import Flask, request, jsonify
from crypto_utils import AESCipher, verify_pow
from Crypto.Util.Padding import unpad

app = Flask(__name__)

CHALLENGE_DATA_FILE = 'challenge_data.json'
INTERNAL_KEY_FILE = 'internal_relay_key.bin'
SESSION_LIMIT = 32

sessions = {}

with open(CHALLENGE_DATA_FILE, 'r') as f:
    challenge_data = json.load(f)

RELAY_KEY = secrets.token_bytes(16)
try:
    if os.path.exists(INTERNAL_KEY_FILE):
        with open(INTERNAL_KEY_FILE, 'rb') as f:
            RELAY_KEY = f.read()
        os.remove(INTERNAL_KEY_FILE)
except Exception:
    pass

cipher = AESCipher(RELAY_KEY)

@app.route('/api/v2/handshake', methods=['GET'])
def handshake():
    session_id = secrets.token_hex(16)
    pow_token = secrets.token_hex(16)
    sessions[session_id] = {
        'pow_token': pow_token,
        'count': 0,
        'created_at': time.time()
    }
    return jsonify({
        "session_id": session_id,
        "pow_token": pow_token,
        "difficulty": 5,
        "expires_in": 300
    })

@app.route('/api/v2/manifest', methods=['GET'])
def get_manifest():
    return jsonify({
        "encrypted_manifest": challenge_data['ciphertext'],
        "iv": challenge_data['iv'],
        "version": "2.6.1-enterprise"
    })

@app.route('/api/v2/telemetry/verify', methods=['POST'])
def verify_telemetry():
    # Cleanup old sessions
    now = time.time()
    to_delete = [sid for sid, s in sessions.items() if now - s['created_at'] > 300]
    for sid in to_delete: del sessions[sid]

    data = request.get_json()
    session_id = request.headers.get('X-Session-ID')
    pow_nonce = request.headers.get('X-Strato-PoW')

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid or expired session"}), 401
    
    session = sessions[session_id]
    
    # Enforce PoW
    if not verify_pow(session['pow_token'], pow_nonce, difficulty=5):
        return jsonify({"error": "PoW verification failed"}), 403

    # Session rate limit to prevent massive parallelization without re-handshaking
    session['count'] += 1
    if session['count'] > SESSION_LIMIT:
        del sessions[session_id]
        return jsonify({"error": "Session limit reached. Re-handshake required"}), 429

    try:
        ct = bytes.fromhex(data['payload'])
        iv = bytes.fromhex(data['iv'])
        
        # Performance benchmark simulation (The actual Oracle)
        start_time = time.time()
        
        # 1. Decrypt raw data
        raw_pt = cipher.decrypt_raw(ct, iv)
        
        try:
            # 2. Layer 1: PKCS#7 Padding Verification
            plaintext = unpad(raw_pt, 16)
            
            # 3. Layer 2: Simulated complex integrity check
            # This creates a timing side-channel: 
            # If padding is CORRECT, the CPU spends time on checksums.
            # If padding is INCORRECT, the function returns early.
            # We add a constant delay to the 'Success' path to mask it,
            # but we leave a gap between 'Padding Error' and 'Checksum Error'.
            
            # Artificial delay for validation logic processing
            time.sleep(0.04)
            
            data_part = plaintext[:-1]
            checksum = plaintext[-1]
            
            # Weighted checksum calculation
            actual_checksum = sum(b * (i + 1) for i, b in enumerate(data_part)) % 256
            
            if actual_checksum != checksum:
                raise ValueError("Checksum mismatch")
            
            # Layer 3: Final Schema Check
            json.loads(data_part.decode('utf-8'))
            
            return jsonify({"status": "error", "code": "E_VAL_7", "rid": secrets.token_hex(4)}), 400
            
        except (ValueError, KeyError, UnicodeDecodeError):
            # Unified status code for all failures: 400 Bad Request
            # The ONLY difference is the response time.
            return jsonify({"status": "error", "code": "E_VAL_7", "rid": secrets.token_hex(4)}), 400
            
    except Exception:
        return jsonify({"status": "error", "code": "E_SYS_1"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)