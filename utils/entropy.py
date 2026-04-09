import math
from collections import Counter

def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    frequencies = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in frequencies.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return entropy
