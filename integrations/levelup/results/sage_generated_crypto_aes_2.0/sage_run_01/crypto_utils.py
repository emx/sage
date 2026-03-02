from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad

class EncryptionError(Exception): pass
class PaddingError(Exception): pass

def encrypt_ctp(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext, AES.block_size))

def decrypt_ctp(key, iv, ciphertext):
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        return unpad(decrypted, AES.block_size)
    except ValueError:
        # Crypto.Util.Padding.unpad raises ValueError on bad padding
        raise PaddingError("Invalid padding")
    except Exception as e:
        raise EncryptionError(str(e))