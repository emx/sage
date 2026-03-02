import os
import json
import zlib
import struct
from Crypto.Cipher import AES

def custom_pad(data):
    pad_len = 16 - (len(data) % 16)
    pad_val = 0x42 ^ pad_len
    # Generate padding sequence: (pad_val^1, pad_val^2, ... pad_val^pad_len)
    padding = bytes([(pad_val ^ i) & 0xff for i in range(1, pad_len + 1)])
    # The last byte of the ciphertext block will be (pad_val ^ 1)
    return data + padding[::-1]

def init():
    key = os.urandom(16)
    with open("key.bin", "wb") as f:
        f.write(key)

    try:
        with open("/flag.txt", "r") as f: 
            flag = f.read().strip()
    except:
        flag = "LEVELUP{BctfRA8SOPvhDbZkQP0_Kkz0kNS55z4q}"

    magic = b"VNGD"
    secret_json = json.dumps({"data": flag}).encode()
    body = magic + secret_json
    crc = struct.pack("<I", zlib.crc32(body) & 0xffffffff)
    
    plaintext = body + crc
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(custom_pad(plaintext))

    with open("challenge_data.json", "w") as f:
        json.dump({"iv": iv.hex(), "ct": ct.hex()}, f)

if __name__ == "__main__":
    init()