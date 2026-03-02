import os
import uuid
import hashlib
import json
import time
from flask import Flask, request, jsonify
from crypto_utils import decrypt_telemetry

app = Flask(__name__)

# Internal system keys
with open('/app/internal.key', 'rb') as f:
    AES_KEY = f.read()

with open('/app/challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

sessions = {}

def generate_trace(error_type):
    # Blind oracle: returns a deterministic hash based on the error type and secret key
    # This hides the specific nature of the error while still providing a side-channel
    return hashlib.sha256(AES_KEY + error_type.encode()).hexdigest()[:16]

@app.route('/api/session', methods=['GET'])
def get_session():
    session_id = str(uuid.uuid4())
    challenge = os.urandom(16).hex()
    sessions[session_id] = {
        "challenge": challenge,
        "expiry": time.time() + 60
    }
    return jsonify({
        "session_id": session_id,
        "challenge": challenge,
        "difficulty": 16,
        "message": "PoW: sha256(challenge + nonce + iv + payload) must start with '0000'"
    })

@app.route('/api/telemetry/logs', methods=['GET'])
def get_logs():
    # The attacker gets the encrypted flag here
    return jsonify({
        "status": "success",
        "data": {
            "encrypted_payload": CHALLENGE_DATA['encrypted_flag']
        }
    })

@app.route('/api/telemetry/process', methods=['POST'])
def process_telemetry():
    data = request.json
    required = ['session_id', 'nonce', 'iv', 'payload']
    if not data or not all(k in data for k in required):
        return jsonify({"status": "rejected", "trace": generate_trace("MALFORMED_REQ")}), 200

    session_id = data['session_id']
    if session_id not in sessions or sessions[session_id]['expiry'] < time.time():
        return jsonify({"status": "rejected", "trace": generate_trace("EXPIRED_SESSION")}), 200

    # Verify Binding Proof-of-Work
    # Hardening: PoW is now bound to the specific ciphertext to prevent pre-computation
    challenge = sessions[session_id]['challenge']
    nonce = data['nonce']
    iv = data['iv']
    payload = data['payload']
    
    work = f"{challenge}{nonce}{iv}{payload}".encode()
    h = hashlib.sha256(work).hexdigest()
    if not h.startswith('0000'):
        return jsonify({"status": "rejected", "trace": generate_trace("INVALID_POW")}), 403

    # Consume session to prevent replay
    del sessions[session_id]

    try:
        iv_bytes = bytes.fromhex(iv)
        payload_bytes = bytes.fromhex(payload)
        
        # 1. Decryption and Padding Check
        plaintext = decrypt_telemetry(iv_bytes, payload_bytes, AES_KEY)
        
        # 2. Schema / Logic Check
        # Decrypted data must start with 'TELE' and be valid JSON
        if not plaintext.startswith(b'TELE'):
             return jsonify({"status": "rejected", "trace": generate_trace("LOGIC_ERR")}), 200
        
        telemetry_obj = json.loads(plaintext[4:].decode('utf-8'))
        if "source" not in telemetry_obj:
            return jsonify({"status": "rejected", "trace": generate_trace("LOGIC_ERR")}), 200
            
        return jsonify({"status": "accepted", "trace": generate_trace("SUCCESS")})

    except ValueError as e:
        # Blind side-channel for Padding Oracle
        if "Padding" in str(e):
            return jsonify({"status": "rejected", "trace": generate_trace("STRUC_ERR")}), 200
        return jsonify({"status": "rejected", "trace": generate_trace("LOGIC_ERR")}), 200
    except Exception:
        return jsonify({"status": "rejected", "trace": generate_trace("LOGIC_ERR")}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)