from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def aes_decrypt_oracle(token_hex, key):
    try:
        data = bytes.fromhex(token_hex)
        if len(data) < 32:
            return False, "ERR_DSAS_000"
            
        iv = data[:16]
        ciphertext = data[16:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        
        # Padding Oracle Point
        try:
            decrypted = unpad(decrypted_padded, 16, style='pkcs7')
        except ValueError:
            # Padding is incorrect
            return False, "ERR_DSAS_001"
            
        # Structural Check
        if not decrypted.startswith(b"CHRONO|"):
            # Padding is correct, but magic bytes are missing
            return False, "ERR_DSAS_002"
            
        return True, "SUCCESS"
    except:
        return False, "ERR_DSAS_999"