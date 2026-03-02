from Crypto.Cipher import AES

def get_dynamic_mask(iv):
    # The padding mask is derived from the first byte of the IV
    return (iv[0] ^ 0x3C) & 0xFF

def PKCS7_pad(data, block_size, iv):
    padding_len = block_size - (len(data) % block_size)
    mask = get_dynamic_mask(iv)
    # Each padding byte is XORed with the dynamic mask
    pad_byte = padding_len ^ mask
    return data + bytes([pad_byte] * padding_len)

def PKCS7_unpad(data, block_size, iv):
    if len(data) == 0:
        raise ValueError("Empty data")
    
    mask = get_dynamic_mask(iv)
    # Reverse the dynamic XOR mask to get the true padding length
    padding_len = data[-1] ^ mask
    
    if padding_len < 1 or padding_len > block_size:
        raise ValueError("Invalid padding length")
    
    # Verify all padding bytes match
    for i in range(1, padding_len + 1):
        if data[-i] ^ mask != padding_len:
            raise ValueError("Invalid padding bytes")
        
    return data[:-padding_len]

def aes_encrypt(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(plaintext)

def aes_decrypt(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)