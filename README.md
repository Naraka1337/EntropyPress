# EntropyPress Pro

A high-fidelity data compression and transmission simulator. This project was built to explore the fundamentals of **Information Theory** and **Lossless Data Compression**.

> [!NOTE]
> **Educational Project:** This tool is designed for learning and demonstration. While it implements industry-standard algorithms from scratch, it prioritizes code readability and mathematical transparency over industrial high-speed performance.

## 🎓 Why this was built
EntropyPress was developed to bypass the "black box" of modern compression libraries. By implementing Huffman and LZW logic from the ground up, we can observe the relationship between **Shannon Entropy $H(X)$** and actual bit-reduction in real-time.

## 🚀 Realistic Use Cases
While modern tools like 7-Zip dominate consumer PCs, the logic in EntropyPress is still the backbone of:
*   **Embedded Systems:** Resource-constrained environments where complex libraries are too heavy.
*   **Satellite & LoRa Communication:** Where simple bit-level ECC (Hamming) is essential for noisy long-range links.
*   **Legacy Data Formats:** Understanding the foundations of GIF (LZW) and JPEG/MP3 (Huffman/DCT) encoding.

## 🛠️ Core Features
*   **Huffman Coding:** Manual tree construction and bit-packed serialization.
*   **Adaptive LZW:** Variable 9-12 bit tokenization with automated dictionary resets.
*   **Noisy Channel Simulation:** A Binary Symmetric Channel (BSC) to test robustness.
*   **Error Correction (ECC):** Hamming (7,4) logic for bit-level data recovery.

## 📊 Educational vs. Industrial
| Feature | EntropyPress (Educational) | 7-Zip / Zstandard (Industrial) |
| :--- | :--- | :--- |
| **Logic** | Pure Huffman / LZW | Multi-stage (LZ77 + Range Coding) |
| **I/O** | Atomic (File-in-RAM) | Streamed (Sliding Windows) |
| **ECC** | Hamming (7,4) | Reed-Solomon / LDPC |
| **Target** | Transparency & Learning | Max Speed & Density |

## Usage
1. `pip install -r requirements.txt`
2. `python main.py`
3. Select a dataset from `/datasets` and experiment with the Noise probability.

## License
MIT

