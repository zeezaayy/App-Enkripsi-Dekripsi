"""
Aplikasi Enkripsi & Dekripsi - Block Cipher + XOR
GUI dengan file explorer + OCR dari gambar (tkinter built-in)

Dependensi opsional untuk fitur OCR:
    pip install pillow pytesseract
    + Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

# OCR — opsional, fitur gambar nonaktif jika tidak terinstall
try:
    from PIL import Image
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

BLOCK_SIZE = 4
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]


# ──────────────────────────────────────────────
# CORE FUNCTIONS
# ──────────────────────────────────────────────

def pad(text: str) -> str:
    while len(text) % BLOCK_SIZE != 0:
        text += " "
    return text


def encrypt(plaintext: str, key: str) -> str:
    if not key:
        raise ValueError("Key tidak boleh kosong.")
    plaintext = pad(plaintext)
    ciphertext = ""
    for i in range(0, len(plaintext), BLOCK_SIZE):
        block = plaintext[i:i + BLOCK_SIZE]
        for j in range(len(block)):
            encrypted_char = ord(block[j]) ^ ord(key[j % len(key)])
            ciphertext += format(encrypted_char, '02x')
    return ciphertext


def decrypt(ciphertext: str, key: str) -> str:
    if not key:
        raise ValueError("Key tidak boleh kosong.")
    ciphertext = ciphertext.strip()
    if len(ciphertext) % 2 != 0:
        raise ValueError("Ciphertext tidak valid (panjang hex harus genap).")
    try:
        bytes_data = bytes.fromhex(ciphertext)
    except ValueError:
        raise ValueError("Ciphertext mengandung karakter non-hex yang tidak valid.")
    plaintext = ""
    for i in range(0, len(bytes_data), BLOCK_SIZE):
        block = bytes_data[i:i + BLOCK_SIZE]
        for j in range(len(block)):
            plaintext += chr(block[j] ^ ord(key[j % len(key)]))
    return plaintext.strip()


def ocr_from_image(path: str) -> str:
    """Ekstrak teks dari file gambar menggunakan Tesseract OCR."""
    img = Image.open(path)
    img = img.convert("L")  # grayscale untuk hasil OCR lebih akurat
    text = pytesseract.image_to_string(img, lang="eng+ind")
    return text.strip()


# ──────────────────────────────────────────────
# GUI APPLICATION
# ──────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enkripsi & Dekripsi — Block Cipher XOR")
        self.resizable(True, True)
        self.minsize(580, 560)
        self.configure(bg="#f5f5f0")
        self._build_ui()
        self.update_idletasks()
        w, h = 660, 640
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        PAD       = 16
        BG        = "#f5f5f0"
        CARD      = "#ffffff"
        BORDER    = "#e0dfd8"
        ACCENT    = "#3266ad"
        FONT      = ("Segoe UI", 10)
        FONT_BOLD = ("Segoe UI", 10, "bold")
        FONT_TITL = ("Segoe UI", 13, "bold")
        FONT_SM   = ("Segoe UI", 9)

        # ── Title bar ──
        title_bar = tk.Frame(self, bg=ACCENT, pady=14)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="Enkripsi & Dekripsi  ·  Block Cipher XOR",
                 bg=ACCENT, fg="white", font=FONT_TITL).pack()
        if not OCR_AVAILABLE:
            tk.Label(title_bar,
                     text="⚠  Fitur gambar nonaktif — install: pip install pillow pytesseract",
                     bg="#2255a0", fg="#ffd580", font=FONT_SM).pack(pady=(4, 0))

        # ── Main container ──
        main = tk.Frame(self, bg=BG, padx=PAD, pady=PAD)
        main.pack(fill="both", expand=True)

        # ── Key row ──
        key_frame = tk.Frame(main, bg=CARD, bd=0, relief="flat",
                             highlightthickness=1, highlightbackground=BORDER)
        key_frame.pack(fill="x", pady=(0, 10))
        inner_key = tk.Frame(key_frame, bg=CARD, padx=12, pady=10)
        inner_key.pack(fill="x")
        tk.Label(inner_key, text="Key (kunci rahasia)", bg=CARD,
                 font=FONT_BOLD, fg="#333").grid(row=0, column=0, sticky="w")
        self.key_var = tk.StringVar()
        self.show_key_var = tk.BooleanVar(value=False)
        self.key_entry = tk.Entry(inner_key, textvariable=self.key_var,
                                  show="●", font=FONT, width=32, bd=1, relief="solid")
        self.key_entry.grid(row=0, column=1, padx=(10, 6), sticky="ew")
        inner_key.columnconfigure(1, weight=1)
        tk.Checkbutton(inner_key, text="Tampilkan", variable=self.show_key_var,
                       command=self._toggle_key, bg=CARD, font=FONT_SM,
                       fg="#555", activebackground=CARD).grid(row=0, column=2)

        # ── Mode tabs ──
        tab_frame = tk.Frame(main, bg=BG)
        tab_frame.pack(fill="x", pady=(0, 6))
        self.mode = tk.StringVar(value="enkripsi")
        for val, label in [("enkripsi", "  Enkripsi  "), ("dekripsi", "  Dekripsi  ")]:
            tk.Radiobutton(tab_frame, text=label, variable=self.mode,
                           value=val, command=self._on_mode_change,
                           bg=BG, activebackground=BG, font=FONT,
                           indicatoron=False, bd=0, relief="flat",
                           selectcolor=ACCENT, fg="#333", activeforeground="#333",
                           padx=12, pady=6).pack(side="left", padx=(0, 4))

        # ── Input section ──
        in_card = tk.Frame(main, bg=CARD, bd=0, highlightthickness=1,
                           highlightbackground=BORDER)
        in_card.pack(fill="both", expand=True, pady=(0, 8))
        in_inner = tk.Frame(in_card, bg=CARD, padx=12, pady=10)
        in_inner.pack(fill="both", expand=True)

        top_row = tk.Frame(in_inner, bg=CARD)
        top_row.pack(fill="x", pady=(0, 6))
        self.input_label = tk.Label(top_row, text="Plaintext", bg=CARD,
                                    font=FONT_BOLD, fg="#333")
        self.input_label.pack(side="left")

        btn_row = tk.Frame(top_row, bg=CARD)
        btn_row.pack(side="right")

        tk.Button(btn_row, text="📂 Buka .txt", command=self._browse_txt,
                  font=FONT_SM, bg=CARD, bd=1, relief="solid",
                  cursor="hand2", padx=8, pady=3).pack(side="left", padx=(0, 6))

        img_state = "normal" if OCR_AVAILABLE else "disabled"
        img_lbl   = "🖼 Buka Gambar" if OCR_AVAILABLE else "🖼 Gambar (install dulu)"
        self.img_btn = tk.Button(btn_row, text=img_lbl, command=self._browse_image,
                                 font=FONT_SM, bg=CARD, bd=1, relief="solid",
                                 cursor="hand2" if OCR_AVAILABLE else "arrow",
                                 padx=8, pady=3, state=img_state,
                                 fg="#333" if OCR_AVAILABLE else "#aaa")
        self.img_btn.pack(side="left", padx=(0, 6))

        tk.Button(btn_row, text="Hapus", command=self._clear_input,
                  font=FONT_SM, bg=CARD, bd=1, relief="solid",
                  cursor="hand2", padx=8, pady=3).pack(side="left")

        self.input_text = scrolledtext.ScrolledText(in_inner, height=7,
                                                    font=("Consolas", 10),
                                                    wrap="word", bd=1, relief="solid")
        self.input_text.pack(fill="both", expand=True)

        self.file_label = tk.Label(in_inner, text="", bg=CARD, font=FONT_SM, fg="#888")
        self.file_label.pack(anchor="w", pady=(4, 0))

        self.img_preview = tk.Label(in_inner, bg=CARD)
        self.img_preview.pack(anchor="w", pady=(2, 0))

        # ── Action button ──
        self.action_btn = tk.Button(main, text="🔒  Enkripsi Sekarang",
                                    command=self._run,
                                    bg=ACCENT, fg="white", font=FONT_BOLD,
                                    bd=0, relief="flat", cursor="hand2",
                                    padx=16, pady=10,
                                    activebackground="#2255a0", activeforeground="white")
        self.action_btn.pack(fill="x", pady=(0, 8))

        # ── Output section ──
        out_card = tk.Frame(main, bg=CARD, bd=0, highlightthickness=1,
                            highlightbackground=BORDER)
        out_card.pack(fill="both", expand=True)
        out_inner = tk.Frame(out_card, bg=CARD, padx=12, pady=10)
        out_inner.pack(fill="both", expand=True)

        out_top = tk.Frame(out_inner, bg=CARD)
        out_top.pack(fill="x", pady=(0, 6))
        self.output_label = tk.Label(out_top, text="Ciphertext (Hasil)",
                                     bg=CARD, font=FONT_BOLD, fg="#333")
        self.output_label.pack(side="left")
        tk.Button(out_top, text="💾 Simpan File", command=self._save_output,
                  font=FONT_SM, bg=CARD, bd=1, relief="solid",
                  cursor="hand2", padx=8, pady=3).pack(side="right", padx=(6, 0))
        tk.Button(out_top, text="Salin", command=self._copy_output,
                  font=FONT_SM, bg=CARD, bd=1, relief="solid",
                  cursor="hand2", padx=8, pady=3).pack(side="right")

        self.output_text = scrolledtext.ScrolledText(out_inner, height=5,
                                                     font=("Consolas", 10),
                                                     wrap="word", bd=1, relief="solid",
                                                     state="disabled", bg="#fafaf8")
        self.output_text.pack(fill="both", expand=True)

    # ──────────────────────────────────────────
    # EVENT HANDLERS
    # ──────────────────────────────────────────

    def _toggle_key(self):
        self.key_entry.config(show="" if self.show_key_var.get() else "●")

    def _on_mode_change(self):
        if self.mode.get() == "enkripsi":
            self.input_label.config(text="Plaintext")
            self.output_label.config(text="Ciphertext (Hasil)")
            self.action_btn.config(text="🔒  Enkripsi Sekarang")
            if OCR_AVAILABLE:
                self.img_btn.config(state="normal", fg="#333", cursor="hand2")
        else:
            self.input_label.config(text="Ciphertext (hex)")
            self.output_label.config(text="Plaintext (Hasil)")
            self.action_btn.config(text="🔓  Dekripsi Sekarang")
            # Tombol gambar nonaktif di mode dekripsi (tidak relevan)
            self.img_btn.config(state="disabled", fg="#aaa", cursor="arrow")
        self._clear_input()
        self._clear_output()

    def _browse_txt(self):
        path = filedialog.askopenfilename(
            title="Pilih file .txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._load_text(content, os.path.basename(path), icon="📄")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file:\n{e}")

    def _browse_image(self):
        if not OCR_AVAILABLE:
            messagebox.showwarning(
                "Library tidak ditemukan",
                "Install terlebih dahulu:\n\n"
                "  pip install pillow pytesseract\n\n"
                "Dan Tesseract engine:\n"
                "  https://github.com/UB-Mannheim/tesseract/wiki"
            )
            return

        ext_list = " ".join(f"*{e}" for e in IMAGE_EXTENSIONS)
        path = filedialog.askopenfilename(
            title="Pilih file gambar",
            filetypes=[
                ("Image files", ext_list),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return

        self.file_label.config(text="⏳  Memproses OCR, harap tunggu...")
        self.update_idletasks()

        try:
            text = ocr_from_image(path)
            if not text:
                messagebox.showwarning(
                    "Teks tidak ditemukan",
                    "OCR tidak menemukan teks di gambar ini.\n"
                    "Pastikan gambar cukup jelas dan mengandung tulisan."
                )
                self.file_label.config(text="")
                return
            self._load_text(text, os.path.basename(path), icon="🖼")
            self._show_thumbnail(path)

        except pytesseract.TesseractNotFoundError:
            messagebox.showerror(
                "Tesseract tidak ditemukan",
                "Tesseract OCR engine belum terinstall atau tidak ada di PATH.\n\n"
                "Download di:\n"
                "  https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                "Setelah install, tambahkan ke PATH sistem,\n"
                "atau set manual di baris berikut dalam kode:\n"
                "  pytesseract.pytesseract.tesseract_cmd = r'C:\\...\\tesseract.exe'"
            )
            self.file_label.config(text="")
        except Exception as e:
            messagebox.showerror("Error OCR", f"Gagal memproses gambar:\n{e}")
            self.file_label.config(text="")

    def _load_text(self, content: str, filename: str, icon: str = "📄"):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", content)
        self.file_label.config(
            text=f"{icon}  {filename}  —  {len(content)} karakter terdeteksi"
        )
        self.img_preview.config(image="", text="")

    def _show_thumbnail(self, path: str):
        try:
            from PIL import ImageTk
            img = Image.open(path)
            img.thumbnail((120, 80))
            self._thumb_ref = ImageTk.PhotoImage(img)
            self.img_preview.config(image=self._thumb_ref)
        except Exception:
            pass  # thumbnail opsional, tidak fatal

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self.file_label.config(text="")
        self.img_preview.config(image="", text="")
        if hasattr(self, "_thumb_ref"):
            self._thumb_ref = None

    def _clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")

    def _set_output(self, text: str):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.config(state="disabled")

    def _run(self):
        key  = self.key_var.get().strip()
        text = self.input_text.get("1.0", "end").strip()
        if not key:
            messagebox.showwarning("Key kosong", "Masukkan key terlebih dahulu.")
            return
        if not text:
            messagebox.showwarning("Input kosong",
                                   "Masukkan teks, buka file .txt, atau buka gambar.")
            return
        try:
            result = encrypt(text, key) if self.mode.get() == "enkripsi" else decrypt(text, key)
            self._set_output(result)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _copy_output(self):
        content = self.output_text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Info", "Tidak ada output untuk disalin.")
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Berhasil", "Teks hasil disalin ke clipboard!")

    def _save_output(self):
        content = self.output_text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Info", "Tidak ada output untuk disimpan.")
            return
        path = filedialog.asksaveasfilename(
            title="Simpan hasil sebagai",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Berhasil", f"File disimpan:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file:\n{e}")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()