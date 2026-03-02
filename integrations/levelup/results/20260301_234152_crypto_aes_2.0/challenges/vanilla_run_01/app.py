import os
import pwd
import time
from flask import Flask, request, jsonify
import crypto_utils

# Security Layer: The service starts as root to read the hardware-protected key,
# then drops privileges to 'ctfuser' before handling any network requests.

def load_secret_key():
    try:
        with open('/app/internal_key.bin', 'rb') as f:
            return f.read()
    except Exception:
        return os.urandom(16)

def drop_privileges():
    try:
        user = pwd.getpwnam('ctfuser')
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)
    except Exception as e:
        print(f"Privilege drop failed: {e}")

# Load key into memory as root
KEY = load_secret_key()
drop_privileges()

app = Flask(__name__)

@app.route('/api/archive/inspect', methods=['GET'])
def inspect_archive():
    """Returns the encrypted telemetry log from the archives."""
    try:
        with open('/app/challenge_data.json', 'r') as f:
            import json
            data = json.load(f)
            return jsonify({"status": "success", "encrypted_log": data['encrypted_log']})
    except Exception:
        return jsonify({"status": "error", "message": "Archive unavailable"}), 500

@app.route('/api/relay/validate', methods=['POST'])
def validate_relay():
    """Validates the integrity of a relay packet."""
    # Constant time processing to prevent simple timing attacks on the JSON parsing itself
    start_time = time.time()
    data = request.get_json()
    
    if not data or 'payload' not in data:
        return jsonify({"status": "error", "code": "ERR_MALFORMED_REQUEST"}), 400

    # The vulnerability is now a blind timing oracle
    # We no longer differentiate between BAD_HEADER and BAD_PADDING in the response code.
    is_valid_structure = crypto_utils.verify_packet_integrity(data['payload'], KEY)
    
    # Enforce a base processing time to normalize response times
    # but verify_packet_integrity adds an additional delay on successful padding
    duration = time.time() - start_time
    if duration < 0.02:
        time.sleep(0.02 - duration)

    return jsonify({"status": "success", "code": "MSG_RECEIVED"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)