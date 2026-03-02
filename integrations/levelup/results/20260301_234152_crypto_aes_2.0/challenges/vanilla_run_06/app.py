import os
import json
import struct
import time
from flask import Flask, request, make_response
from Crypto.Cipher import AES
from crypto_utils import orion_unpad, get_crc32, nibble_swap

app = Flask(__name__)

# Global state
SECRET_KEY = b""
ENCRYPTED_CONFIG = ""

def initialize_service():
    global SECRET_KEY, ENCRYPTED_CONFIG
    try:
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
            SECRET_KEY = bytes.fromhex(data['key'])
            ENCRYPTED_CONFIG = data['config_iv_ct']
    except Exception as e:
        print(f"Initialization error: {e}")
        exit(1)

@app.route('/api/v1/relay/config', methods=['GET'])
def get_config():
    return json.dumps({"config": ENCRYPTED_CONFIG})

@app.route('/api/v1/relay/process', methods=['POST'])
def process_packet():
    try:
        req_data = request.get_json()
        if not req_data or 'data' not in req_data:
            return make_response('{"status":"error","message":"ERR_NO_DATA"}', 400)
            
        payload = req_data.get('data', '')
        raw = bytes.fromhex(payload)
        if len(raw) < 32 or len(raw) % 16 != 0:
            return make_response('{"status":"error","message":"ERR_MALFORMED"}', 400)
        
        iv = raw[:16]
        ct = raw[16:]
        
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ct)
        
        trace_id = os.urandom(8).hex()
        
        try:
            # Step 1: Context-Aware Unpadding
            plaintext = orion_unpad(decrypted, iv)
            
            # Step 2: Integrity Verification (Nibble-Swapped CRC32)
            if len(plaintext) < 4:
                raise ValueError("Truncated payload")
                
            data_part = plaintext[:-4]
            checksum_part = plaintext[-4:]
            
            # CRC is calculated on the nibble-swapped data part
            if get_crc32(nibble_swap(data_part)) != struct.unpack("<I", checksum_part)[0]:
                # Oracle Case: Correct padding, Incorrect integrity
                # Signal: Key order [status, code, trace], trace is UPPERCASE
                resp_obj = {}
                resp_obj["status"] = "error"
                resp_obj["code"] = 403
                resp_obj["trace"] = trace_id.upper()
                resp = make_response(json.dumps(resp_obj), 200)
                resp.headers['Content-Type'] = 'application/json'
                return resp
            
            return make_response(json.dumps({"status": "success", "message": "Command processed"}), 200)

        except ValueError:
            # Oracle Case: Incorrect padding
            # Signal: Key order [status, trace, code], trace is lowercase
            resp_obj = {}
            resp_obj["status"] = "error"
            resp_obj["trace"] = trace_id.lower()
            resp_obj["code"] = 403
            resp = make_response(json.dumps(resp_obj), 200)
            resp.headers['Content-Type'] = 'application/json'
            return resp

    except Exception as e:
        return make_response('{"status":"error","message":"ERR_INTERNAL"}', 500)

@app.route('/api/v1/system/status', methods=['GET'])
def status():
    return json.dumps({
        "system": "Orion-Link Relay Node", 
        "version": "3.1.2-STABLE",
        "integrity": "Nibble-Swapped-CRC32",
        "security": "Context-Aware Dynamic Masking"
    })

if __name__ == '__main__':
    initialize_service()
    app.run(host='0.0.0.0', port=5000)