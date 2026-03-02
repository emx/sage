import json
import secrets
from crypto_utils import AESCipher

def calculate_checksum(data):
    return sum(b * (i + 1) for i, b in enumerate(data)) % 256

def init():
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{DEBUG_FLAG}"

    manifest = {
        "session_id": secrets.token_hex(8),
        "node": "THETA-RELAY-9",
        "flag": flag,
        "integrity": "HIGH"
    }
    
    key = secrets.token_bytes(16)
    with open('internal_relay_key.bin', 'wb') as f:
        f.write(key)

    json_bytes = json.dumps(manifest).encode()
    
    # Weighted Checksum
    checksum = calculate_checksum(json_bytes)
    payload = json_bytes + bytes([checksum])

    cipher = AESCipher(key)
    iv, ct = cipher.encrypt(payload)
    
    data = {
        "ciphertext": ct,
        "iv": iv
    }
    
    with open('challenge_data.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    init()