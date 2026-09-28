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
- ⚡ Cached processing to avoid unnecessary re-processing
- 🚀 Streamlit Community Cloud-ready deployment
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

## Deploy to Streamlit Community Cloud

This repository is ready for deployment on Streamlit Community Cloud.

1. Sign in to Streamlit Community Cloud with GitHub.
2. Create a new app.
3. Select this repository and the `main` branch.
4. Set the entrypoint to `pdf_clearer.py`.
5. Deploy.

The repository includes `requirements.txt` for Python packages and `packages.txt` for the Linux Tesseract dependency required by OCR. Text-to-speech is intended primarily for local use because it depends on the host machine's speech engine.

## How it works

1. Upload a PDF.
2. Choose enhancement settings from the sidebar.
3. Direct text is extracted first using PyMuPDF.
4. Only pages without selectable text are sent through OCR.
5. The selected preview page is rendered on demand instead of rendering the entire PDF immediately.
6. A cleaned PDF is generated only when the user requests an export.
7. Cached results prevent repeated work during normal Streamlit interactions.

## Tech stack

- **Python**
- **Streamlit**
- **PyMuPDF**
- **Pillow**
- **Tesseract OCR / pytesseract**
- **pyttsx3**

## License

MIT
