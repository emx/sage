def custom_pad(data, block_size):
    padding_len = block_size - (len(data) % block_size)
    # Hardening: Use a non-standard XOR-masked padding scheme
    padding_val = padding_len ^ 0x13
    return data + bytes([padding_val] * padding_len)

def custom_validate_padding(data):
    if len(data) == 0:
        return False
    padding_val = data[-1]
    padding_len = padding_val ^ 0x13
    if padding_len < 1 or padding_len > 16:
        return False
    for i in range(1, padding_len + 1):
        if data[-i] != padding_val:
            return False
    return True

def custom_unpad(data):
    padding_val = data[-1]
    padding_len = padding_val ^ 0x13
    return data[:-padding_len]