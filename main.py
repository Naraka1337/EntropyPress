import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from algorithms import huffman, lzw
from channel import noise, hamming
from utils.entropy import calculate_entropy

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Data Compression & Info Theory")
        self.geometry("900x650")
        
        self.grid_columnconfigure((0, 1), weight=1)
        
        self.title_label = ctk.CTkLabel(self, text="EntropyPress", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.file_path_var = ctk.StringVar()
        self.file_label = ctk.CTkLabel(self.file_frame, text="Selected File: None", font=ctk.CTkFont(size=14))
        self.file_label.pack(side="left", padx=10, pady=10)
        
        self.btn_select_file = ctk.CTkButton(self.file_frame, text="Select File", command=self.select_file)
        self.btn_select_file.pack(side="right", padx=10, pady=10)

        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.algo_var = ctk.StringVar(value="Huffman")
        self.algo_label = ctk.CTkLabel(self.settings_frame, text="Algorithm:")
        self.algo_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.algo_dropdown = ctk.CTkOptionMenu(self.settings_frame, values=["Huffman", "LZW"], variable=self.algo_var)
        self.algo_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.bonus_var = ctk.BooleanVar(value=False)
        self.bonus_checkbox = ctk.CTkCheckBox(self.settings_frame, text="Simulate Noisy Channel & Error Correction (Hamming 7,4)", variable=self.bonus_var)
        self.bonus_checkbox.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.btn_compress = ctk.CTkButton(self.action_frame, text="Compress", command=self.compress_wrap, fg_color="green", hover_color="darkgreen")
        self.btn_compress.pack(side="left", padx=20, pady=10, expand=True)

        self.btn_decompress = ctk.CTkButton(self.action_frame, text="Decompress", command=self.decompress_wrap, fg_color="orange", hover_color="darkorange")
        self.btn_decompress.pack(side="right", padx=20, pady=10, expand=True)
        
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        
        self.results_text = ctk.CTkTextbox(self.results_frame, state="disabled")
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def log(self, msg):
        self.results_text.configure(state="normal")
        self.results_text.insert("end", msg + "\n")
        self.results_text.see("end")
        self.results_text.configure(state="disabled")

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path_var.set(file_path)
            self.file_label.configure(text=f"Selected File: {os.path.basename(file_path)}")
            
    def compress_wrap(self):
        fp = self.file_path_var.get()
        if not fp:
            messagebox.showerror("Error", "Please select a file first.")
            return
        threading.Thread(target=self.do_compress, args=(fp,)).start()
        
    def decompress_wrap(self):
        fp = self.file_path_var.get()
        if not fp:
            messagebox.showerror("Error", "Please select a file first.")
            return
        threading.Thread(target=self.do_decompress, args=(fp,)).start()

    def do_compress(self, filepath):
        self.btn_compress.configure(state="disabled")
        self.btn_decompress.configure(state="disabled")
        try:
            self.log(f"--- Starting Compression on {os.path.basename(filepath)} ---")
            
            with open(filepath, "rb") as f:
                data = f.read()
                
            orig_size = len(data)
            entropy = calculate_entropy(data)
            self.log(f"Original Size: {orig_size} bytes")
            self.log(f"Entropy H(X): {entropy:.4f} bits/symbol")
            
            algo = self.algo_var.get()
            t0 = time.time()
            if algo == "Huffman":
                comp_data = huffman.compress(data)
            else:
                comp_data = lzw.compress(data)
            t1 = time.time()
            
            comp_size = len(comp_data)
            if comp_size == 0:
                self.log(f"Compressed Size: 0 bytes. Original was empty.")
            else:
                self.log(f"Compressed Size ({algo}): {comp_size} bytes")
                self.log(f"Compression Ratio: {(orig_size/comp_size if comp_size > 0 else 0):.2f}:1")
            self.log(f"Execution Time: {(t1-t0)*1000:.2f} ms")
            
            if self.bonus_var.get():
                self.log("\n[BONUS] Applying Hamming (7,4) Error Correction Encoding...")
                t_enc_0 = time.time()
                enc_data = hamming.encode(comp_data)
                t_enc_1 = time.time()
                
                self.log(f"[BONUS] Encoding Time: {(t_enc_1-t_enc_0)*1000:.2f} ms")
                self.log(f"[BONUS] Encoded Payload Size: {len(enc_data)} bytes")
                
                self.log("[BONUS] Simulating Binary Symmetric Channel (Noise=0.01)...")
                noisy_data = noise.binary_symmetric_channel(enc_data, 0.01)
                
                out_path = filepath + f".{algo.lower()}_noisy"
                with open(out_path, "wb") as f:
                    f.write(noisy_data)
                self.log(f"Saved NOISY compressed file to: {os.path.basename(out_path)}")
            else:
                out_path = filepath + f".{algo.lower()}"
                with open(out_path, "wb") as f:
                    f.write(comp_data)
                self.log(f"Saved securely compressed file to: {os.path.basename(out_path)}")
                
            self.log("Compression Complete!\n")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
        finally:
            self.btn_compress.configure(state="normal")
            self.btn_decompress.configure(state="normal")

    def do_decompress(self, filepath):
        self.btn_compress.configure(state="disabled")
        self.btn_decompress.configure(state="disabled")
        try:
            self.log(f"--- Starting Decompression on {os.path.basename(filepath)} ---")
            
            with open(filepath, "rb") as f:
                data = f.read()

            self.log(f"Input file size: {len(data)} bytes")
                
            comp_data = data
            if self.bonus_var.get():
                self.log("\n[BONUS] Decoding Hamming (7,4) and Correcting Errors...")
                t_dec_0 = time.time()
                comp_data, errors_corrected = hamming.decode(data)
                t_dec_1 = time.time()
                self.log(f"[BONUS] Decoding Time: {(t_dec_1-t_dec_0)*1000:.2f} ms")
                self.log(f"[BONUS] Number of bit errors corrected: {errors_corrected}")
            
            algo = self.algo_var.get()
            t0 = time.time()
            if algo == "Huffman":
                decomp_data = huffman.decompress(comp_data)
            else:
                decomp_data = lzw.decompress(comp_data)
            t1 = time.time()
            
            self.log(f"Decompressed Size: {len(decomp_data)} bytes")
            self.log(f"Decompression Execution Time: {(t1-t0)*1000:.2f} ms")
            
            out_path = filepath + ".dec"
            with open(out_path, "wb") as f:
                f.write(decomp_data)
            self.log(f"Saved decompressed file to: {os.path.basename(out_path)}")
                
            self.log("Decompression Complete!\n")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log(f"ERROR: {str(e)}")
        finally:
            self.btn_compress.configure(state="normal")
            self.btn_decompress.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
