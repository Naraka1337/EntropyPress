import random

def binary_symmetric_channel(data: bytes, error_probability: float = 0.01) -> bytes:
    """Flips bits in the byte array with the given error probability."""
    if error_probability <= 0:
        return data
        
    noisy_data = bytearray()
    for byte in data:
        noisy_byte = byte
        for bit_index in range(8):
            if random.random() < error_probability:
                noisy_byte ^= (1 << bit_index)
        noisy_data.append(noisy_byte)
    return bytes(noisy_data)
