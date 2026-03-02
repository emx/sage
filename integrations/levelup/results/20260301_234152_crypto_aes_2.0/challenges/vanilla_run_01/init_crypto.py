import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def init():
    with open('/flag.txt', 'r') as f:
        flag = f.read().strip()
    
    key = os.urandom(16)
    header = "VANGUARD_RELAY_v1.0:"
    plaintext = (header + flag).encode()
    
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw_ciphertext = cipher.encrypt(pad(plaintext, 16))
    
    # Apply the mask during initialization so it's decryptable by the app
    mask = iv[0]
    # For the first block, mask is iv[0]. For subsequent blocks N, mask is ciphertext[N-1][0]
    # We must apply this logic to the encrypted stream
    masked_blocks = []
    prev_block_first_byte = iv[0]
    
    # AES-CBC gives us raw_ciphertext. The app does: 
    # Decrypt(C_n) ^ C_{n-1} ^ Mask_n
    # So we must pre-XOR our plaintext with the mask before standard AES encryption
    
    p_padded = pad(plaintext, 16)
    blocks = [p_padded[i:i+16] for i in range(0, len(p_padded), 16)]
    
    encrypted_payload = b""
    curr_iv = iv
    for block in blocks:
        mask = curr_iv[0]
        # Apply mask to plaintext before standard CBC encryption
        masked_block = bytes([b ^ mask for b in block])
        cipher = AES.new(key, AES.MODE_CBC, curr_iv)
        enc_block = cipher.encrypt(masked_block)
        encrypted_payload += enc_block
        curr_iv = enc_block

    ciphertext = iv + encrypted_payload
    
    with open('/app/challenge_data.json', 'w') as f:
        json.dump({"encrypted_log": ciphertext.hex()}, f)
    
    with open('/app/internal_key.bin', 'wb') as f:
        f.write(key)

if __name__ == '__main__':
    init()