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

import sys

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Load Icon
        try:
            if getattr(sys, 'frozen', False):
                # If running as EXE, look in the temp folder where PyInstaller extracts
                icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
            else:
                icon_path = "Icon.ico"
            
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass # Silent fail if icon is missing

        self.title("EntropyPress Pro - v1.0.0")
        self.geometry("1000x750")
        
        self.grid_columnconfigure((0, 1), weight=1)
        
        # Header with Version
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="EntropyPress", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(side="left")
        
        self.ver_label = ctk.CTkLabel(self.header_frame, text="v1.0.0", font=ctk.CTkFont(size=12))
        self.ver_label.pack(side="left", padx=10, pady=(10, 0))
        
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
        
        self.results_text = ctk.CTkTextbox(self.results_frame, state="disabled", font=ctk.CTkFont(family="Consolas", size=13))
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Progress & Status Bar
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, mode="indeterminate", height=10)
        self.progress_bar.pack(side="top", fill="x", padx=10, pady=(5, 2))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="System Ready", font=ctk.CTkFont(size=12, slant="italic"))
        self.status_label.pack(side="bottom", anchor="w", padx=15, pady=2)
        
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
            self.status_label.configure(text="Processing...", text_color="orange")
            self.progress_bar.start()
            
            self.log(f"--- [TASK] Compression: {os.path.basename(filepath)} ---")
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Source file not found: {filepath}")

            with open(filepath, "rb") as f:
                data = f.read()
                
            orig_size = len(data)
            entropy = calculate_entropy(data)
            self.log(f"[*] Original Size: {orig_size:,} bytes")
            self.log(f"[*] Shannon Entropy: {entropy:.4f} bits/symbol")
            
            algo = self.algo_var.get()
            t0 = time.time()
            if algo == "Huffman":
                comp_data = huffman.compress(data)
            else:
                comp_data = lzw.compress(data)
            t1 = time.time()
            
            comp_size = len(comp_data)
            elapsed = (t1-t0)*1000
            
            if comp_size == 0:
                self.log(f"[!] Warning: Compressed file is empty.")
            else:
                ratio = (orig_size/comp_size if comp_size > 0 else 0)
                self.log(f"[*] Algorithm: {algo}")
                self.log(f"[*] Compressed Size: {comp_size:,} bytes")
                self.log(f"[*] Compression Ratio: {ratio:.2f}:1")
            self.log(f"[*] Time Elapsed: {elapsed:.2f} ms")
            
            if self.bonus_var.get():
                self.log("\n[BONUS] Applying Hamming (7,4) ECC...")
                enc_data = hamming.encode(comp_data)
                
                self.log("[BONUS] Simulating BSC (p=0.01)...")
                noisy_data = noise.binary_symmetric_channel(enc_data, 0.01)
                
                out_path = filepath + f".{algo.lower()}_noisy"
                with open(out_path, "wb") as f:
                    f.write(noisy_data)
            else:
                out_path = filepath + f".{algo.lower()}"
                with open(out_path, "wb") as f:
                    f.write(comp_data)
            
            self.status_label.configure(text="Compression Successful!", text_color="green")
            self.log(f"\n[SUCCESS] File saved as: {os.path.basename(out_path)}")
            messagebox.showinfo("Success", f"Compression complete!\nSaved to: {os.path.basename(out_path)}")
            
        except Exception as e:
            self.status_label.configure(text="Error occurred", text_color="red")
            self.log(f"[ERROR] {str(e)}")
            messagebox.showerror("Production Error", f"An error occurred during compression:\n{str(e)}")
        finally:
            self.progress_bar.stop()
            self.progress_bar.set(0)
            self.btn_compress.configure(state="normal")
            self.btn_decompress.configure(state="normal")

    def do_decompress(self, filepath):
        self.btn_compress.configure(state="disabled")
        self.btn_decompress.configure(state="disabled")
        try:
            self.status_label.configure(text="Decoding...", text_color="orange")
            self.progress_bar.start()
            
            self.log(f"--- [TASK] Decompression: {os.path.basename(filepath)} ---")
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Source file not found: {filepath}")

            with open(filepath, "rb") as f:
                data = f.read()

            self.log(f"[*] Encoded Size: {len(data):,} bytes")
                
            comp_data = data
            if self.bonus_var.get():
                self.log("\n[BONUS] ECC Decoding...")
                comp_data, errors_corrected = hamming.decode(data)
                self.log(f"[BONUS] Bit errors corrected: {errors_corrected}")
            
            algo = self.algo_var.get()
            t0 = time.time()
            if algo == "Huffman":
                decomp_data = huffman.decompress(comp_data)
            else:
                decomp_data = lzw.decompress(comp_data)
            t1 = time.time()
            
            self.log(f"[*] Decompressed Size: {len(decomp_data):,} bytes")
            self.log(f"[*] Time Elapsed: {(t1-t0)*1000:.2f} ms")
            
            out_path = filepath + ".dec"
            with open(out_path, "wb") as f:
                f.write(decomp_data)
            
            self.status_label.configure(text="Decompression Successful!", text_color="green")
            self.log(f"\n[SUCCESS] File recovered to: {os.path.basename(out_path)}")
            messagebox.showinfo("Success", f"Decompression complete!\nRestored: {os.path.basename(out_path)}")
                
        except Exception as e:
            self.status_label.configure(text="Error occurred", text_color="red")
            self.log(f"[ERROR] {str(e)}")
            messagebox.showerror("Production Error", f"Failed to decompress file:\n{str(e)}")
        finally:
            self.progress_bar.stop()
            self.progress_bar.set(0)
            self.btn_compress.configure(state="normal")
            self.btn_decompress.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
