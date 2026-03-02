import os
import json
import secrets
from crypto_utils import AESCipher

def main():
    key = os.urandom(16)
    system_token = secrets.token_hex(16)
    
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        flag = "LEVELUP{DEBUG_FLAG_LOCAL_TEST}"
    
    cipher = AESCipher(key)
    system_blob = json.dumps({"system_token": system_token, "security_level": "elevated"})
    encrypted_blob = cipher.encrypt(system_blob)
    
    with open('challenge_data.json', 'w') as f:
        json.dump({
            "encrypted_system_blob": encrypted_blob,
            "service_key": key.hex(),
            "flag": flag
        }, f)

if __name__ == '__main__':
    main()