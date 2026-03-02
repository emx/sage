import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt_packet(data_dict, key):
    import json
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = json.dumps(data_dict).encode('utf-8')
    padded_data = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    return (iv + ciphertext).hex()

def decrypt_packet(packet_bytes, key):
    if len(packet_bytes) < 32:
        raise ValueError("Malformed structure")
    
    iv = packet_bytes[:16]
    ciphertext = packet_bytes[16:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    
    try:
        return unpad(decrypted_padded, AES.block_size)
    except ValueError:
        raise ValueError("Padding is incorrect")