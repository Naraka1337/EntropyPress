# EntropyPress Pro

A data compression and transmission simulation utility focused on Information Theory and Lossless Data Compression.

## Purpose
EntropyPress is an educational tool for demonstrating the implementation of Huffman Coding and LZW. It allows for the observation of the relationship between Shannon Entropy H(X) and actual bit-reduction in a controlled environment.

## Realistic Use Cases
The logic implemented in this tool is applicable in:
*   Embedded Systems: Resource-constrained environments with limited memory.
*   Satellite & LoRa Communication: Bit-level ECC (Hamming) for noisy data links.
*   Legacy Data Formats: Core logic of GIF (LZW) and JPEG/MP3 (Huffman) encoding.

## Core Features
*   Huffman Coding: Manual tree construction and bit-packed serialization.
*   Adaptive LZW: Variable 9-12 bit tokenization with dictionary resets.
*   Noisy Channel Simulation: Binary Symmetric Channel (BSC) for robustness testing.
*   Error Correction: Hamming (7,4) implementation for data recovery.

## Comparison: Educational vs. Industrial
| Feature | EntropyPress (Educational) | Industry Standard (7-Zip/Zstd) |
| :--- | :--- | :--- |
| Logic | Pure Huffman / LZW | Multi-stage (LZ77 + Range Coding) |
| I/O | Atomic (File-in-RAM) | Streamed (Sliding Windows) |
| ECC | Hamming (7,4) | Reed-Solomon / LDPC |
| Target | Transparency | Performance & Density |

## Usage
1. pip install -r requirements.txt
2. python main.py
3. Select a dataset from /datasets.

## License
MIT
