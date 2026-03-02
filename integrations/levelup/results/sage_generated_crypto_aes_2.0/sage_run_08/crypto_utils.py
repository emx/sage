from Crypto.Cipher import AES

class PaddingError(Exception):
    pass

def pkcs7_unpad(data):
    if not data:
        raise PaddingError("Invalid padding length")
    padding_len = data[-1]
    if padding_len < 1 or padding_len > 16:
        raise PaddingError("Invalid padding length")
    padding = data[-padding_len:]
    if padding != bytes([padding_len] * padding_len):
        raise PaddingError("Invalid padding bytes")
    return data[:-padding_len]

def aes_decrypt(combined_ct, key):
    iv = combined_ct[:16]
    ciphertext = combined_ct[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt_padded = cipher.decrypt(ciphertext)
    return pkcs7_unpad(pt_padded)