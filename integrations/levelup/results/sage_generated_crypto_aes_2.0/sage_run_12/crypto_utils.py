from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt_telemetry(data_bytes, key):
    iv = AES.get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data_bytes, 16))
    return iv.hex(), ciphertext.hex()

def decrypt_telemetry(iv, ciphertext, key):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    # The built-in unpad raises ValueError("Padding is incorrect.") if check fails
    return unpad(decrypted, 16)