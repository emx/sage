import os
import json
import binascii
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__)

class AES_Manager:
    def __init__(self, key):
        self.key = key

    def decrypt(self, hex_ciphertext):
        try:
            data = binascii.unhexlify(hex_ciphertext)
            if len(data) < 32:
                return False, "Invalid payload length"
            
            iv = data[:16]
            ciphertext = data[16:]
            
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            
            try:
                # Padding Oracle: Distinguish between padding failure and other errors
                unpad(decrypted, 16)
                return True, "Valid manifest structure"
            except ValueError:
                return False, "Invalid structure"
        except Exception:
            return False, "Malformed hex encoding"

OSM_KEY = None
ENCRYPTED_MANIFEST = None
manager = None

def load_challenge_data():
    global OSM_KEY, ENCRYPTED_MANIFEST, manager
    try:
        with open('challenge_data.json', 'r') as f:
            data = json.load(f)
            OSM_KEY = binascii.unhexlify(data['key'])
            ENCRYPTED_MANIFEST = data['encrypted_flag']
        manager = AES_Manager(OSM_KEY)
    except Exception as e:
        print(f"Error loading challenge data: {e}")

# Initialize data at startup
load_challenge_data()

@app.route('/api/osm/v1/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "system": "Orbital-Sync Manifest (OSM) v2.4",
        "node": "GND-STATION-09"
    })

@app.route('/api/osm/v1/archive', methods=['GET'])
def get_archive():
    return jsonify({
        "manifest_id": "FS-9921-ALPHA",
        "blob": ENCRYPTED_MANIFEST,
        "note": "Encrypted flight recorder data for audit purposes."
    })

@app.route('/api/osm/v1/verify', methods=['POST'])
def verify_manifest():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400
            
        user_input = request.json.get('blob', '')
        if not user_input:
            return jsonify({"status": "error", "message": "Missing blob"}), 400
        
        success, message = manager.decrypt(user_input)
        
        if success:
            return jsonify({"status": "success", "message": "Manifest integrity verified"}), 200
        else:
            # The leak: Specifically returns "Invalid structure" on padding failure
            return jsonify({"status": "error", "message": f"Integrity check failed: {message}"}), 400
    except Exception as e:
        return jsonify({# "status": "error", "message": "Internal processing error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)