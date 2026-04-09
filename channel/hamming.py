def encode(data: bytes) -> bytes:
    bit_string = ''.join(f'{b:08b}' for b in data)
    pad_len = (4 - len(bit_string) % 4) % 4
    bit_string += '0' * pad_len
    
    encoded_bits = []
    for i in range(0, len(bit_string), 4):
        d1 = int(bit_string[i])
        d2 = int(bit_string[i+1])
        d3 = int(bit_string[i+2])
        d4 = int(bit_string[i+3])
        
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
        
        encoded_bits.extend([p1, p2, d1, p3, d2, d3, d4])
        
    encoded_bit_string = ''.join(str(b) for b in encoded_bits)
    pad_len_8 = (8 - len(encoded_bit_string) % 8) % 8
    encoded_bit_string += '0' * pad_len_8
    
    out_bytes = bytearray()
    for i in range(0, len(encoded_bit_string), 8):
        out_bytes.append(int(encoded_bit_string[i:i+8], 2))
        
    return bytes([pad_len, pad_len_8]) + bytes(out_bytes)

def decode(data: bytes) -> tuple[bytes, int]:
    if len(data) < 2:
        return b"", 0
    pad_len = data[0]
    pad_len_8 = data[1]
    
    bit_string = ''.join(f'{b:08b}' for b in data[2:])
    if pad_len_8 > 0:
        bit_string = bit_string[:-pad_len_8]
        
    decoded_bits = []
    errors_corrected = 0
    
    for i in range(0, len(bit_string), 7):
        chunk = bit_string[i:i+7]
        if len(chunk) < 7:
            break
            
        c = [int(b) for b in chunk]
        p1, p2, d1, p3, d2, d3, d4 = c
        
        s1 = p1 ^ d1 ^ d2 ^ d4
        s2 = p2 ^ d1 ^ d3 ^ d4
        s3 = p3 ^ d2 ^ d3 ^ d4
        
        error_pos = s1 * 1 + s2 * 2 + s3 * 4
        if error_pos > 0:
            errors_corrected += 1
            c[error_pos - 1] ^= 1
            
        decoded_bits.extend([c[2], c[4], c[5], c[6]])
        
    decoded_str = ''.join(str(b) for b in decoded_bits)
    if pad_len > 0:
        decoded_str = decoded_str[:-pad_len]
        
    out_bytes = bytearray()
    for i in range(0, len(decoded_str), 8):
        out_bytes.append(int(decoded_str[i:i+8], 2))
        
    return bytes(out_bytes), errors_corrected
