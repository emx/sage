import os
import json
import hashlib
import uuid
import time
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from crypto_utils import custom_validate_padding, custom_unpad

app = Flask(__name__)

# Load pre-generated challenge data
with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

KEY = bytes.fromhex(CHALLENGE_DATA['key'])
FLAG_CT = CHALLENGE_DATA['encrypted_flag']

# In-memory storage for PoW challenges
active_challenges = {}

def heavy_integrity_check(data):
    # Simulate a computationally expensive integrity/header check
    # This creates a timing side-channel for the padding oracle
    hashlib.pbkdf2_hmac('sha256', data, b'telemetry_salt_v2', 80000)
    return data.startswith(b'{"origin":"VO-')

@app.route('/api/telemetry/archive', methods=['GET'])
def get_archive():
    return jsonify({
        "status": "success",
        "archive_id": str(uuid.uuid4()),
        "enc_log": FLAG_CT
    })

@app.route('/api/request_work', methods=['GET'])
def request_work():
    challenge = os.urandom(8).hex()
    work_token = str(uuid.uuid4())
    active_challenges[work_token] = challenge
    return jsonify({"work_token": work_token, "challenge": challenge, "difficulty": 5})

@app.route('/api/telemetry/validate', methods=['POST'])
def validate_telemetry():
    data = request.get_json()
    if not data or 'work_token' not in data or 'solution' not in data or 'ciphertext' not in data:
        return jsonify({"error": "Missing parameters"}), 400

    # PoW Validation
    token = data['work_token']
    solution = data['solution']
    if token not in active_challenges:
        return jsonify({"error": "Invalid or expired work token"}), 403
    
    challenge = active_challenges.pop(token)
    h = hashlib.sha256((challenge + solution).encode()).hexdigest()
    # Increased PoW difficulty to 20-bit prefix
    if not h.startswith('00000'):
        return jsonify({ "error": "Invalid Proof-of-Work solution" }), 403

    try:
        ct_bytes = bytes.fromhex(data['ciphertext'])
        if len(ct_bytes) < 32 or len(ct_bytes) % 16 != 0:
            return jsonify({"error": "Malformed ciphertext length"}), 400
        
        iv = ct_bytes[:16]
        actual_ct = ct_bytes[16:]
        
        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        pt = cipher.decrypt(actual_ct)
        
        # Oracle Step: Validate Padding (Fast Path)
        if not custom_validate_padding(pt):
            # Return generic error immediately on padding failure
            return jsonify({"status": "error", "message": "Security verification failed", "ref": str(uuid.uuid4())}), 200
        
        # Oracle Step: Validate Header (Slow Path)
        # This path only executes if padding is valid, creating a timing side-channel
        if not heavy_integrity_check(pt):
            return jsonify({"status": "error", "message": "Security verification failed", "ref": str(uuid.uuid4())}), 200

        return jsonify({"status": "success", "message": "Telemetry block valid"}), 200

    except Exception:
        return jsonify({"status": "error", "message": "Internal processing error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)