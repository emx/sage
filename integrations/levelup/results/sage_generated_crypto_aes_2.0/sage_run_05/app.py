import os
import json
import hashlib
import secrets
import time
import zlib
import struct
import threading
from flask import Flask, request, jsonify, make_response
from Crypto.Cipher import AES

class AtomicCounter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.value += 1
            return self.value

class HardenedVanguard:
    def __init__(self, key):
        self.key = key
        self.secret = secrets.token_bytes(32)
        self.request_counter = AtomicCounter()

    def custom_unpad(self, data):
        """
        Vanguard V4 Padding Scheme:
        pad_len = 16 - (L % 16)
        pad_val = 0x42 ^ pad_len
        byte_i = pad_val ^ i (where i is 1-indexed from end)
        """
        if len(data) < 16:
            return None
        
        # Recover pad_len from last byte: data[-1] = (0x42 ^ pad_len) ^ 1
        pad_len = data[-1] ^ 0x43
        if pad_len < 1 or pad_len > 16:
            return None
        
        pad_val = 0x42 ^ pad_len
        for i in range(1, pad_len + 1):
            if data[-i] != ((pad_val ^ i) & 0xff):
                return None
        return data[:-pad_len]

    def verify_integrity(self, iv, ct):
        """
        Oracle logic with multiple internal failure states.
        0: Padding Invalid
        1: Integrity/Format Invalid (CRC/Magic/JSON)
        3: Success
        """
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ct)
            
            # Step 1: Check Custom Padding
            plaintext = self.custom_unpad(decrypted)
            if plaintext is None:
                return 0
            
            # Step 2: Check CRC32 and Magic (Merged state to minimize info leak)
            if len(plaintext) < 8: # 4 magic + 4 crc
                return 1
            
            data_body = plaintext[:-4]
            target_crc = struct.unpack("<I", plaintext[-4:])[0]
            if (zlib.crc32(data_body) & 0xffffffff) != target_crc:
                return 1
            
            if not data_body.startswith(b"VNGD"):
                return 1
            
            try:
                json.loads(data_body[4:].decode())
                return 3
            except:
                return 1
        except:
            return 0

class ProofOfWork:
    def __init__(self, difficulty=20):
        self.difficulty = difficulty

    def generate_challenge(self):
        return secrets.token_hex(8)

    def verify(self, challenge, nonce):
        h = hashlib.sha256((challenge + str(nonce)).encode()).hexdigest()
        # 20 bits = 5 hex zeros
        return h.startswith('00000')

app = Flask(__name__)

with open('key.bin', 'rb') as f:
    AES_KEY = f.read()

with open('challenge_data.json', 'r') as f:
    CHALLENGE_DATA = json.load(f)

cipher_suite = HardenedVanguard(AES_KEY)
pow_handler = ProofOfWork(difficulty=20)

@app.route('/api/vanguard/telemetry', methods=['GET'])
def get_telemetry():
    # Removed session_salt to prevent pre-computation of ETags
    return jsonify({
        "status": "operational",
        "iv": CHALLENGE_DATA['iv'],
        "payload": CHALLENGE_DATA['ct'],
        "hint": "ETag integrity rotating window enabled (v4.0-Enterprise)"
    })

@app.route('/api/vanguard/verify', methods=['POST'])
def verify_sequence():
    data = request.get_json()
    if not data or 'iv' not in data or 'payload' not in data or 'pow_nonce' not in data or 'pow_challenge' not in data:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    if not pow_handler.verify(data['pow_challenge'], data['pow_nonce']):
        return jsonify({"status": "error", "message": "Invalid PoW"}), 403

    try:
        iv = bytes.fromhex(data['iv'])
        payload = bytes.fromhex(data['payload'])
        
        error_state = cipher_suite.verify_integrity(iv, payload)
        
        # Obfuscated Side-Channel: ETag depends on a rolling window
        # The oracle hash changes every 10 requests, requiring the attacker
        # to re-calibrate their "Fail" vs "Pass" signals constantly.
        count = cipher_suite.request_counter.increment()
        window = count // 10
        
        state_hash = hashlib.sha256(
            cipher_suite.secret + 
            str(error_state).encode() + 
            str(window).encode()
        ).hexdigest()
        
        status_code = 403
        res_data = {"status": "error", "message": "Access Denied"}
        
        if error_state == 3:
            status_code = 200
            res_data = {"status": "success", "message": "Sequence Accepted"}
        
        resp = make_response(jsonify(res_data), status_code)
        resp.headers['ETag'] = state_hash
        # Constant time delay to hinder automation and emphasize PoW bottleneck
        time.sleep(0.05)
        return resp

    except Exception as e:
        return jsonify({"status": "error", "message": "Internal processing failure"}), 500

@app.route('/api/vanguard/pow_challenge', methods=['GET'])
def get_pow():
    challenge = pow_handler.generate_challenge()
    return jsonify({"challenge": challenge, "difficulty_bits": 20})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)