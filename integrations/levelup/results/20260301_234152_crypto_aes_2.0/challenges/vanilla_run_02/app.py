import os
import json
import time
import random
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# Global state loaded once at startup
try:
    with open('challenge_data.json', 'r') as f:
        data = json.load(f)
        ADMIN_PACKET_HEX = data['ciphertext']
        SECRET_KEY = bytes.fromhex(data['key'])
        INITIAL_INTEGRITY = data['integrity_token']
except Exception:
    ADMIN_PACKET_HEX = ""
    SECRET_KEY = os.urandom(16)
    INITIAL_INTEGRITY = 0

def is_padding_valid(decrypted):
    if len(decrypted) == 0:
        return False
    pad_len = decrypted[-1]
    if pad_len <= 0 or pad_len > 16:
        return False
    return decrypted[-pad_len:] == bytes([pad_len]) * pad_len

def calculate_checksum(data_bytes):
    # Hardened Checksum: Bitwise rotation and FNV-1a style multiplication
    # This prevents simple XOR-based forgery and requires reversing the algorithm.
    res = 0xDEADBEEF
    for b in data_bytes:
        res = ((res << 7) | (res >> 25)) & 0xFFFFFFFF
        res ^= b
        res = (res * 0x1000193) & 0xFFFFFFFF
    return res

@app.route('/api/ledger/status', methods=['GET'])
def get_status():
    return jsonify({
        "description": "Horizon-Link Admin Deployment Ledger",
        "status": "Archived",
        "packet_id": "AL-99283",
        "encrypted_payload": ADMIN_PACKET_HEX,
        "integrity_token": INITIAL_INTEGRITY
    })

@app.route('/api/ledger/validate', methods=['POST'])
def validate_packet():
    # Base latency to limit brute force speed
    time.sleep(0.02)
    
    data = request.get_json()
    if not data or 'payload' not in data or 'integrity_token' not in data:
        return jsonify({"status": "error", "message": "Malformed request structure"}), 400

    try:
        ct = bytes.fromhex(data['payload'])
        token = int(data['integrity_token'])
    except Exception:
        return jsonify({"status": "error", "message": "Data encoding error"}), 400

    # Requirement 1: Checksum verification (Must be calculated for every modification)
    if calculate_checksum(ct) != token:
        # Small delay to prevent distinguishing checksum failure via timing
        time.sleep(0.01)
        return jsonify({"status": "error", "message": "Packet corrupted: Integrity mismatch"}), 400

    if len(ct) < 32 or len(ct) % 16 != 0:
        return jsonify({"status": "error", "message": "Packet corrupted: Invalid block alignment"}), 400
    
    iv = ct[:16]
    ciphertext = ct[16:]
    
    try:
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        # SUBTLE TIMING ORACLE
        # 1. Padding check
        valid_padding = is_padding_valid(decrypted)
        
        # 2. Timing Signal: Reduce delta from 80ms to 25ms
        if valid_padding:
            time.sleep(0.025)
            
        # 3. Triangular Jitter: Harder to filter statistically than uniform jitter
        # Mode is set to 0.025 to create a probability density peak that masks the signal
        time.sleep(random.triangular(0.0, 0.060, 0.025))
        
        # Uniform error message
        if valid_padding and decrypted.startswith(b"AETHER_CMD:"):
             return jsonify({"status": "success", "message": "Command integrity verified"}), 200
        
        return jsonify({"status": "error", "message": "Signal noise: Verification failed"}), 200

    except Exception:
        return jsonify({"status": "error", "message": "Internal processing error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)