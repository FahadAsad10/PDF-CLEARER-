# PDF Clearer ✨

A Streamlit app that makes difficult PDF documents easier to read, search, listen to, and export.

## Features

- 📄 Upload PDF documents
- 🔍 Adjustable rendering zoom
- 🌈 Contrast enhancement
- 💡 Brightness adjustment
- 🌙 Dark reading mode
- 🔎 OCR text extraction with Tesseract
- 📝 Direct text extraction for digital PDFs
- 🗣️ Optional text-to-speech
- 📥 Export enhanced pages as a new PDF
- ⚡ Cached processing to avoid re-processing the same document on every Streamlit interaction
- 🖥️ Automatic Tesseract detection on Windows/Linux/macOS-compatible environments

## Run locally

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

OCR is optional, but recommended for scanned PDFs.

**Windows:** install Tesseract and, if it is not detected automatically, set:

```text
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Ubuntu/Debian:**

```bash
sudo apt install tesseract-ocr
```

**macOS:**

```bash
brew install tesseract
```

### 3. Start the app

```bash
streamlit run pdf_clearer.py
```

Then open the local URL shown by Streamlit.

## How it works

1. Upload a PDF.
2. Choose enhancement settings from the sidebar.
3. PDF pages are rendered and enhanced with PyMuPDF and Pillow.
4. Text is extracted directly when possible, or with OCR for scanned pages.
5. Preview the enhanced pages.
6. Download a cleaned PDF or use the extracted text.

## Tech stack

- **Python**
- **Streamlit**
- **PyMuPDF**
- **Pillow**
- **Tesseract OCR / pytesseract**
- **pdfplumber**
- **pyttsx3**

## License

MIT
