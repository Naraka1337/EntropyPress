import struct
import heapq
from collections import Counter

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
        
    def __lt__(self, other):
        return self.freq < other.freq

def build_tree(data):
    if not data: return None
    freq = Counter(data)
    heap = [Node(char, f) for char, f in freq.items()]
    heapq.heapify(heap)
    
    if len(heap) == 1:
        n = Node(None, 0)
        n.left = heap[0]
        n.right = Node((heap[0].char + 1) % 256, 0) # Dummy right child
        return n
        
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
        
    return heap[0]

def build_codes(node, prefix="", codebook=None):
    if codebook is None: codebook = {}
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        build_codes(node.left, prefix + "0", codebook)
        build_codes(node.right, prefix + "1", codebook)
    return codebook

def serialize_tree(node):
    if node.char is not None:
        return "1" + f"{node.char:08b}"
    else:
        return "0" + serialize_tree(node.left) + serialize_tree(node.right)

def compress(data: bytes) -> bytes:
    if not data: return b""
    tree = build_tree(data)
    codebook = build_codes(tree)
    
    header = struct.pack(">Q", len(data))
    encoded_str = serialize_tree(tree) + "".join(codebook[b] for b in data)
    pad_len = (8 - len(encoded_str) % 8) % 8
    encoded_str += "0" * pad_len
    
    out = bytearray(header)
    for i in range(0, len(encoded_str), 8):
        out.append(int(encoded_str[i:i+8], 2))
        
    return bytes(out)

def decompress(data: bytes) -> bytes:
    if not data: return b""
    orig_length = struct.unpack(">Q", data[:8])[0]
    
    encoded_data = data[8:]
    bit_string = "".join(f"{b:08b}" for b in encoded_data)
    bit_iterator = iter(bit_string)
    
    def deserialize_tree():
        try:
            bit = next(bit_iterator)
        except StopIteration:
            return None
        if bit == '1':
            char_bits = "".join(next(bit_iterator) for _ in range(8))
            return Node(int(char_bits, 2), 0)
        else:
            left = deserialize_tree()
            right = deserialize_tree()
            n = Node(None, 0)
            n.left = left
            n.right = right
            return n

    root = deserialize_tree()
    if root is None: return b""
    
    out = bytearray()
    curr = root
    
    while len(out) < orig_length:
        bit = next(bit_iterator)
        if bit == "0": curr = curr.left
        else: curr = curr.right
        
        if curr.char is not None:
            out.append(curr.char)
            curr = root
            
    return bytes(out)
