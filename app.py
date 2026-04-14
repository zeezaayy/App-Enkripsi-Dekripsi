"""
Aplikasi Enkripsi & Dekripsi - Block Cipher XOR
Web App (Flask + Tesseract OCR)
"""

import os
import io
from flask import Flask, request, jsonify, render_template, send_file
from PIL import Image
import pytesseract

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # maks upload 10MB

BLOCK_SIZE = 4


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

pytesseract.pytesseract.tesseract_cmd = "/run/current-system/sw/bin/tesseract"
def ocr_from_image(file_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(file_bytes))
    img = img.convert("L")
    text = pytesseract.image_to_string(img, lang="eng+ind")
    return text.strip()


# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/encrypt", methods=["POST"])
def api_encrypt():
    data = request.get_json()
    plaintext = data.get("text", "").strip()
    key = data.get("key", "").strip()
    if not plaintext:
        return jsonify({"error": "Teks tidak boleh kosong."}), 400
    if not key:
        return jsonify({"error": "Key tidak boleh kosong."}), 400
    try:
        result = encrypt(plaintext, key)
        return jsonify({"result": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/decrypt", methods=["POST"])
def api_decrypt():
    data = request.get_json()
    ciphertext = data.get("text", "").strip()
    key = data.get("key", "").strip()
    if not ciphertext:
        return jsonify({"error": "Ciphertext tidak boleh kosong."}), 400
    if not key:
        return jsonify({"error": "Key tidak boleh kosong."}), 400
    try:
        result = decrypt(ciphertext, key)
        return jsonify({"result": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/upload-txt", methods=["POST"])
def api_upload_txt():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang diupload."}), 400
    file = request.files["file"]
    if not file.filename.endswith(".txt"):
        return jsonify({"error": "Hanya file .txt yang didukung."}), 400
    try:
        content = file.read().decode("utf-8")
        return jsonify({"text": content, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": f"Gagal membaca file: {str(e)}"}), 400


@app.route("/api/upload-image", methods=["POST"])
def api_upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang diupload."}), 400
    file = request.files["file"]
    allowed = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({"error": "Format gambar tidak didukung."}), 400
    try:
        file_bytes = file.read()
        text = ocr_from_image(file_bytes)
        if not text:
            return jsonify({"error": "Tidak ada teks yang terdeteksi di gambar."}), 400
        return jsonify({"text": text, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": f"Gagal memproses gambar: {str(e)}"}), 400


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json()
    content = data.get("content", "")
    filename = data.get("filename", "hasil.txt")
    buf = io.BytesIO(content.encode("utf-8"))
    buf.seek(0)
    return send_file(buf, as_attachment=True,
                     download_name=filename,
                     mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
