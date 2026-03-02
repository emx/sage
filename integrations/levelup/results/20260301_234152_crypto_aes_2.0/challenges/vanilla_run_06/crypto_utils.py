from binascii import crc32

def nibble_swap(data):
    # Swaps high and low nibbles of each byte
    return bytes(((b & 0x0F) << 4) | ((b & 0xF0) >> 4) for b in data)

def orion_pad(data, iv, block_size=16):
    # Dynamic mask based on IV context
    mask = (iv[0] ^ iv[-1] ^ 16) & 0xFF
    pad_len = block_size - (len(data) % block_size)
    padding = bytes([pad_len ^ mask] * pad_len)
    return data + padding

def orion_unpad(data, iv):
    if not data or len(iv) != 16:
        raise ValueError("Invalid state")
    mask = (iv[0] ^ iv[-1] ^ 16) & 0xFF
    pad_val_raw = data[-1]
    pad_len = pad_val_raw ^ mask
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Invalid padding length")
    for i in range(1, pad_len + 1):
        if data[-i] ^ mask != pad_len:
            raise ValueError("Invalid padding bytes")
    return data[:-pad_len]

def get_crc32(data):
    return crc32(data) & 0xFFFFFFFF