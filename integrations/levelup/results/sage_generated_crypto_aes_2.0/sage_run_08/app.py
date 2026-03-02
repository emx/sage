import os
import json
import hashlib
import secrets
import time
import hmac
from flask import Flask, request, jsonify
from crypto_utils import aes_decrypt, PaddingError

app = Flask(__name__)

# Secure PoW Configuration
POW_SECRET = secrets.token_bytes(16)
POW_DIFFICULTY = '00000' 
POW_TTL = 30  # Challenges expire after 30s

# Load challenge data generated during build
try:
    with open('challenge_data.json', 'r') as f:
        data = json.load(f)
        ENCRYPTED_FLAG = data['encrypted_flag']
        AES_KEY = bytes.fromhex(data['key'])
except FileNotFoundError:
    ENCRYPTED_FLAG = ""
    AES_KEY = os.urandom(16)

def generate_challenge():
    ts = str(int(time.time()))
    sig = hmac.new(POW_SECRET, ts.encode(), hashlib.sha256).hexdigest()[:12]
    return f"{ts}.{sig}"

def verify_pow(challenge, nonce):
    try:
        ts, sig = challenge.split('.')
        # 1. Verify HMAC integrity of the challenge
        expected_sig = hmac.new(POW_SECRET, ts.encode(), hashlib.sha256).hexdigest()[:12]
        if not hmac.compare_digest(sig, expected_sig):
            return False
        # 2. Check expiration
        if int(time.time()) - int(ts) > POW_TTL:
            return False
        # 3. Verify Work
        h = hashlib.sha256((challenge + nonce).encode()).hexdigest()
        return h.startswith(POW_DIFFICULTY)
    except Exception:
        return False

@app.route('/api/v1/telemetry/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "operational",
        "subsystem": "Ignition-Link Relay",
        "packet": ENCRYPTED_FLAG,
        "pow_challenge": generate_challenge(),
        "pow_difficulty": POW_DIFFICULTY
    })

@app.route('/api/v1/telemetry/relay', methods=['POST'])
def relay_telemetry():
    nonce = request.headers.get('X-PoW-Nonce', '')
    challenge = request.headers.get('X-PoW-Challenge', '')
    
    # FIXED: Server-side PoW verification with signed challenges
    if not verify_pow(challenge, nonce):
        return jsonify({
            "error": "ERR_POW_INVALID",
            "challenge": generate_challenge(),
            "instruction": f"Solve PoW: sha256(challenge + nonce) starts with '{POW_DIFFICULTY}'"
        }), 401

    req_data = request.get_json()
    if not req_data or 'data' not in req_data:
        return jsonify({"error": "ERR_MALFORMED_REQUEST"}), 400

    try:
        ct_bytes = bytes.fromhex(req_data['data'])
        if len(ct_bytes) < 32 or len(ct_bytes) % 16 != 0:
            return jsonify({"error": "ERR_SIGNAL_LOST"}), 500

        # --- Multi-Stage Timing Oracle ---
        # We add jitter to make the side-channel harder to measure over high-latency networks
        jitter = (secrets.randbelow(5000) / 1000000.0) # 0-5ms jitter
        
        try:
            # Stage 1: PKCS7 Padding Check
            plaintext = aes_decrypt(ct_bytes, AES_KEY)
            
            # Stage 2: Sync-word check (Internal structure check)
            if plaintext.startswith(b"TLMv2"):
                # Path A: Valid Padding + Valid Magic (Slowest)
                time.sleep(0.08 + jitter)
            else:
                # Path B: Valid Padding + Invalid Magic (Medium)
                time.sleep(0.03 + jitter)
            
            # Final check: Format
            json.loads(plaintext[5:].decode('utf-8'))
            return jsonify({"status": "SUCCESS", "msg": "Telemetry parity verified"}), 200

        except PaddingError:
            # Path C: Invalid Padding (Fastest path - no sleep)
            pass
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Path B successor
            pass
        
        return jsonify({"error": "ERR_SIGNAL_LOST"}), 500

    except Exception:
        return jsonify({"error": "ERR_SIGNAL_LOST"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)