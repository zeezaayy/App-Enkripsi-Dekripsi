# Aplikasi Enkripsi & Dekripsi
Aplikasi enkripsi dan dekripsi teks berbasis GUI menggunakan metode **Block Cipher XOR**.
Mendukung input dari teks langsung, file `.txt`, maupun gambar (via OCR).

---

## Fitur
- Enkripsi & dekripsi teks dengan Block Cipher XOR
- Input dari teks langsung, file `.txt`, atau gambar (PNG, JPG, dll.)
- OCR otomatis untuk membaca teks dari gambar
- Simpan hasil ke file `.txt`
- Tampilan GUI yang mudah digunakan

---

## Cara Install & Jalankan (Windows)

### Cara Cepat
1. Download semua file di repo ini (klik tombol hijau **Code** → **Download ZIP**)
2. Extract ZIP
3. Double-click file **`INSTALL_DAN_JALANKAN.bat`**
4. Ikuti instruksi yang muncul

Script akan otomatis install semua yang dibutuhkan.

### Cara Manual
Pastikan sudah install:
- [Python 3.x](https://www.python.org/downloads/) — centang **"Add Python to PATH"** saat install
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) — untuk fitur baca teks dari gambar

Lalu jalankan di terminal:
```bash
pip install pillow pytesseract
python enkripsi_dekripsi_gui.py
```

---

## Struktur File
```
├── enkripsi_dekripsi_gui.py      # Aplikasi utama
├── INSTALL_DAN_JALANKAN.bat      # Script installer otomatis (Windows)
└── README.md                     # Dokumentasi ini
```

---

## Teknologi
- Python 3
- Tkinter (GUI)
- Pillow + Pytesseract (OCR)
- Metode enkripsi: Block Cipher XOR
