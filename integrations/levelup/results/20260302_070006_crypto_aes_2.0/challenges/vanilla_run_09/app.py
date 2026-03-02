import os
import json
import time
import random
import hashlib
from flask import Flask, request, jsonify, Response
from crypto_utils import decrypt_packet

app = Flask(__name__)

# Load pre-generated challenge data
with open('challenge_data.json', 'r') as f:
    challenge_data = json.load(f)

AES_KEY = bytes.fromhex(challenge_data['key'])
ENCRYPTED_ADMIN_PACKET = challenge_data['encrypted_packet']

# Advanced state management for rate limiting and stealth mode
STATE = {
    'limits': {},
    'errors': {},     # IP: [timestamps]
    'stealth_until': {} # IP: timestamp
}

def get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr) or "127.0.0.1"

def is_state_restricted():
    ip = get_ip()
    now = time.time()
    
    # 1. Standard Rate Limiter (5 requests per second)
    STATE['limits'].setdefault(ip, [])
    STATE['limits'][ip] = [t for t in STATE['limits'][ip] if now - t < 1.0]
    if len(STATE['limits'][ip]) >= 5:
        return "Rate limit exceeded", 429
    STATE['limits'][ip].append(now)

    # 2. Stealth Mode Check
    # If the user is in 'Stealth Mode', we add massive random jitter to destroy timing signals
    if ip in STATE['stealth_until'] and now < STATE['stealth_until'][ip]:
        return None, "STEALTH"

    return None, None

def record_padding_error():
    ip = get_ip()
    now = time.time()
    STATE['errors'].setdefault(ip, [])
    STATE['errors'][ip] = [t for t in STATE['errors'][ip] if now - t < 30.0]
    STATE['errors'][ip].append(now)
    
    # If more than 20 padding errors occur in 30 seconds, trigger Stealth Mode for 60 seconds
    if len(STATE['errors'][ip]) > 20:
        STATE['stealth_until'][ip] = now + 60.0

@app.route('/api/telemetry/packet', methods=['GET'])
def get_packet():
    return jsonify({"packet": ENCRYPTED_ADMIN_PACKET})

@app.route('/api/telemetry/verify', methods=['POST'])
def verify_packet():
    err_msg, mode = is_state_restricted()
    if err_msg:
        return jsonify({"status": "Error", "message": err_msg}), 429

    data = request.get_json()
    if not data or 'packet' not in data:
        return jsonify({"status": "Error", "message": "Missing packet data"}), 400

    # Hardening: Require an integrity hash to prevent lazy automated tools
    # The hash is simply sha256(packet_hex)
    client_hash = request.headers.get('X-Integrity-Hash')
    packet_hex = data['packet']
    expected_hash = hashlib.sha256(packet_hex.encode()).hexdigest()
    
    if client_hash != expected_hash:
        return jsonify({"status": "Error", "message": "Integrity check failed"}), 403

    try:
        packet_bytes = bytes.fromhex(packet_hex)
        
        # Decryption - will raise ValueError if PKCS7 padding is invalid
        plaintext = decrypt_packet(packet_bytes, AES_KEY)
        
        # --- VALID PADDING PATH ---
        # Timing: Success takes ~100ms
        base_delay = 0.100
        
        # Business logic
        try:
            decoded = json.loads(plaintext.decode('utf-8'))
            if decoded.get('type') == 'admin_config':
                time.sleep(base_delay)
                return jsonify({"status": "Success", "message": "Telemetry received"})
        except:
            pass
        
        # If JSON is invalid but padding was correct, we still use the 'Success' delay
        time.sleep(base_delay + random.uniform(0, 0.005))
        return Response('{"status":"Error","message":"Invalid packet format"}', status=400, mimetype='application/json')
            
    except ValueError:
        # --- INVALID PADDING PATH ---
        # Timing: Failure takes ~20ms
        record_padding_error()
        
        # If in stealth mode, add massive jitter to destroy the timing oracle
        delay = 0.020
        if mode == "STEALTH":
            delay = random.uniform(0.020, 0.150)
        else:
            delay += random.uniform(0, 0.005)
            
        time.sleep(delay)
        return Response('{"status":"Error","message":"Invalid packet format"}', status=400, mimetype='application/json')
        
    except Exception:
        return jsonify({"status": "Error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)