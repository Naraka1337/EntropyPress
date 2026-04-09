def compress(data: bytes) -> bytes:
    if not data: return b""
    
    # Constants
    CLEAR_CODE = 256
    EOI_CODE = 257
    MAX_DICT_SIZE = 4096 # Standard LZW limit (12-bit)
    
    dictionary = {bytes([i]): i for i in range(256)}
    dict_size = 258
    
    w = bytes([data[0]])
    bit_string = ""
    bit_len = 9
    
    # Initial Clear Code
    bit_string += f"{CLEAR_CODE:0{bit_len}b}"
    
    for i in range(1, len(data)):
        b = bytes([data[i]])
        wb = w + b
        if wb in dictionary:
            w = wb
        else:
            bit_string += f"{dictionary[w]:0{bit_len}b}"
            
            if dict_size < MAX_DICT_SIZE:
                dictionary[wb] = dict_size
                dict_size += 1
                if dict_size > (1 << bit_len):
                    bit_len += 1
            else:
                # Dictionary full: Signal a clear if we were starting to struggle
                # To keep it simple for the ECU project, we just stop growing 
                # or reset. Let's do a reset for better adaptability.
                bit_string += f"{CLEAR_CODE:0{bit_len}b}"
                dictionary = {bytes([i]): i for i in range(256)}
                dict_size = 258
                bit_len = 9
                
            w = b
            
    if w:
        bit_string += f"{dictionary[w]:0{bit_len}b}"
    
    bit_string += f"{EOI_CODE:0{bit_len}b}"
        
    pad_len = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * pad_len
    
    out = bytearray([pad_len])
    for i in range(0, len(bit_string), 8):
        out.append(int(bit_string[i:i+8], 2))
        
    return bytes(out)

def decompress(data: bytes) -> bytes:
    if not data: return b""
    
    CLEAR_CODE = 256
    EOI_CODE = 257
    
    pad_len = data[0]
    bit_string = "".join(f"{b:08b}" for b in data[1:])
    if pad_len > 0:
        bit_string = bit_string[:-pad_len]
        
    dictionary = {i: bytes([i]) for i in range(256)}
    dict_size = 258
    bit_len = 9
    idx = 0
    
    def get_next_code():
        nonlocal idx, bit_len
        if idx + bit_len > len(bit_string): return None
        val = int(bit_string[idx:idx+bit_len], 2)
        idx += bit_len
        return val

    out = bytearray()
    w = b""
    
    while True:
        val = get_next_code()
        if val is None or val == EOI_CODE:
            break
            
        if val == CLEAR_CODE:
            dictionary = {i: bytes([i]) for i in range(256)}
            dict_size = 258
            bit_len = 9
            val = get_next_code()
            if val is None or val == EOI_CODE: break
            w = dictionary[val]
            out.extend(w)
            continue
            
        if val in dictionary:
            entry = dictionary[val]
        elif val == dict_size:
            entry = w + bytes([w[0]])
        else:
            raise ValueError(f"Bad compressed sequence: val {val}")
            
        out.extend(entry)
        
        # Add to dictionary
        if dict_size < 4096:
            dictionary[dict_size] = w + bytes([entry[0]])
            dict_size += 1
            if dict_size == (1 << bit_len) and bit_len < 12:
                bit_len += 1
                
        w = entry
        
    return bytes(out)
