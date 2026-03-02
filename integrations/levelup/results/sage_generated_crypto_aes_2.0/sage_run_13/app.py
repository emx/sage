import os
import json
import hashlib
import time
from flask import Flask, request, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

class AetherSecurityError(Exception):
    pass

class PaddingError(AetherSecurityError):
    pass

class IntegrityError(AetherSecurityError):
    pass

class AetherCipher:
    def __init__(self, key):
        self.key = key

    def _get_mask(self, iv):
        # Dynamic mask derived from the IV to prevent static-mask exploitation
        return iv[0] ^ 0x42

    def _pad(self, data, iv):
        mask = self._get_mask(iv)
        pad_len = 16 - (len(data) % 16)
        # Masked PKCS7-style padding
        return data + bytes([pad_len ^ mask] * pad_len)

    def _unpad(self, data, iv):
        if len(data) == 0:
            raise PaddingError()
        mask = self._get_mask(iv)
        pad_val = data[-1] ^ mask
        if pad_val < 1 or pad_val > 16:
            raise PaddingError()
        # Strict constant-time-ish verification of all padding bytes
        for i in range(1, pad_val + 1):
            if data[-i] ^ mask != pad_val:
                raise PaddingError()
        return data[:-pad_val]

    def encrypt(self, plaintext):
        iv = AES.get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(self._pad(plaintext.encode(), iv))
        return iv + ct

    def decrypt(self, iv, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt_padded = cipher.decrypt(ciphertext)
        return self._unpad(pt_padded, iv)

# Load encrypted flag and key
CHALLENGE_JSON = "challenge_data.json"
if os.path.exists(CHALLENGE_JSON):
    with open(CHALLENGE_JSON, "r") as f:
        data = json.load(f)
        ENCRYPTED_FLAG = data["ENCRYPTED_FLAG"]
        GLOBAL_KEY = bytes.fromhex(data["GLOBAL_KEY"])
else:
    ENCRYPTED_FLAG = ""
    GLOBAL_KEY = os.urandom(32)

cipher_suite = AetherCipher(GLOBAL_KEY)

@app.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({
        "status": "operational",
        "version": "4.0.0-PRO-SHIELD",
        "manifest_id": hashlib.sha1(ENCRYPTED_FLAG.encode()).hexdigest()[:8],
        "vault_blob": ENCRYPTED_FLAG
    })

@app.route('/api/v1/manifest/verify', methods=['POST'])
def verify_manifest():
    data = request.get_json()
    if not data or 'payload' not in data or 'nonce' not in data:
        return jsonify({"status": "error", "code": "MISSING_PARAMS"}), 200

    payload_hex = data['payload']
    nonce = str(data['nonce'])
    
    # Binding Proof-of-Work (20 bits)
    # Now binds the PoW to the specific payload, preventing pre-computation
    combined = (nonce + payload_hex).encode()
    check = hashlib.sha256(combined).hexdigest()
    if not check.startswith("00000"):
        return jsonify({"status": "error", "code": "POW_INSUFFICIENT"}), 200

    try:
        raw_data = bytes.fromhex(payload_hex)
        if len(raw_data) < 32 or len(raw_data) % 16 != 0:
            return jsonify({"status": "error", "code": "MALFORMED_BLOB"}), 200
        
        iv = raw_data[:16]
        ciphertext = raw_data[16:]
        
        try:
            decrypted_bytes = cipher_suite.decrypt(iv, ciphertext)
            
            # Secondary Oracle: Integrity/Structure check
            try:
                manifest = json.loads(decrypted_bytes.decode())
                if not isinstance(manifest, dict) or manifest.get("id", "").find("AETHER") == -1:
                    raise IntegrityError()
            except:
                raise IntegrityError()
                
            return jsonify({"status": "success", "code": "MANIFEST_VALIDATED"}), 200

        except PaddingError:
            # Subtly different error code for padding vs integrity
            return jsonify({"status": "error", "code": "ERR_SIG_INVALID"}), 200
        except IntegrityError:
            # Subtly different error code for integrity failure
            return jsonify({"status": "error", "code": "ERR_MSG_INVALID"}), 200

    except Exception:
        return jsonify({"status": "error", "code": "SYSTEM_FAULT"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)