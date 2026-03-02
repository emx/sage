from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class PaddingError(Exception): pass
class FormatError(Exception): pass

def aes_decrypt(ciphertext, key, iv):
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        # unpad will throw ValueError if padding is incorrect
        return unpad(decrypted, AES.block_size, style='pkcs7')
    except ValueError:
        raise PaddingError("Invalid padding")
    except Exception:
        raise FormatError("Decryption failure")