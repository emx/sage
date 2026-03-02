import os
import json
from Crypto.Cipher import AES

def complex_pad(data, block_size, last_iv_block):
    pad_len = block_size - (len(data) % block_size)
    padding = bytearray()
    # Reverse of the oracle logic
    for i in range(1, pad_len + 1):
        padding.insert(0, pad_len ^ last_iv_block[(16-i) % 16])
    return data + bytes(padding)

def init():
    key = os.urandom(32)
    iv = os.urandom(16)

    try:
        with open('/flag.txt', 'rb') as f:
            flag = f.read().strip()
    except Exception:
        flag = b"LEVELUP{0lPXKA09Yz4HryMskegrG2sxwZtFJIYI}"

    packet_data = b"AETHERIS-TLM:" + flag + b":END"
    
    # We need the last block of ciphertext (or IV for single block) to pad correctly
    # Since we pad the final block, we use a temporary cipher to simulate the CBC chain
    dummy_cipher = AES.new(key, AES.MODE_CBC, iv)
    # Calculate blocks before the last one to find the IV for the last block
    raw_blocks = [packet_data[i:i+16] for i in range(0, len(packet_data), 16)]
    
    # In this case, packet_data is 13+32+4 = 49 bytes. 
    # Blocks: 16, 16, 16, 1 (remaining). Total 4 blocks + padding.
    # The 'iv' for the padding logic is the 4th ciphertext block.
    # For simplicity, we'll just encrypt normally and use the actual chain.
    
    cipher_init = AES.new(key, AES.MODE_CBC, iv)
    full_pt_no_pad = packet_data
    # This is slightly complex because padding depends on the previous ciphertext block
    # We iterate block by block
    ciphertext = b""
    curr_iv = iv
    for i in range(0, len(full_pt_no_pad), 16):
        block = full_pt_no_pad[i:i+16]
        if len(block) < 16:
            block = complex_pad(block, 16, curr_iv)
        c = AES.new(key, AES.MODE_CBC, curr_iv).encrypt(block)
        ciphertext += c
        curr_iv = c
    
    # If it was perfectly aligned, we still need a full block of padding
    if len(ciphertext) == len(full_pt_no_pad):
        block = complex_pad(b"", 16, curr_iv)
        ciphertext += AES.new(key, AES.MODE_CBC, curr_iv).encrypt(block)

    with open('challenge_data.json', 'w') as f:
        json.dump({
            "key": key.hex(),
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex()
        }, f)

if __name__ == '__main__':
    init()