# EntropyPress

A compression utility implementing Huffman and LZW algorithms from scratch. Built for Information Theory and Data Compression (Spring 2026).

## Overview
EntropyPress provides a standalone environment for testing lossless compression and error correction models. It bypasses all external libraries to implement core coding logic directly.

### Core Features
*   **Huffman Coding:** Variable-length prefix codes with bit-packed tree serialization.
*   **Adaptive LZW:** 9-12 bit variable-length token dictionary with automated resets (Clear Codes).
*   **Information Metrics:** Real-time Shannon Entropy $H(X)$ calculation.
*   **Robustness Simulation:** Hamming (7,4) ECC passed through a tuned Binary Symmetric Channel (BSC).

## Implementation Details

### 1. Huffman Serialization
To minimize overhead on small files, the Huffman implementation uses a pre-order tree bit-stream:
- `0` for internal nodes.
- `1` followed by `8 bits` for leaf characters.
- Followed by the compressed payload and an 8-byte original size header.

### 2. Adaptive LZW
The LZW implementation handles dictionary expansion by monitoring the current bit-depth:
- Starts at 9 bits.
- Scales to 12 bits as the dictionary fills.
- Emits a **Clear Code (256)** and resets when the 4096-entry limit is reached, allowing it to adapt to local data patterns.

### 3. Error Correction Pipeline
1. **Compress:** File is reduced via Huffman/LZW.
2. **FEC Encode:** Encoded into Hamming (7,4) blocks.
3. **Channel:** Passed through a noisy environment (bit-flip probability).
4. **Correction:** Syndrome analysis detects and fixes bit errors.
5. **Decompress:** Original file restoration.

## Usage

### Setup
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

## Datasets
- `sample.txt`: Text data for character distribution testing.
- `repetitive.txt`: High-redundancy data for LZW benchmarking.
- `image.bmp`: Binary structure testing for spatial pattern compression.

## Performance Analysis
Performance metrics (Entropy, Speed, Ratio) are logged in the GUI and exported to `test_report.md`.

## License
MIT

