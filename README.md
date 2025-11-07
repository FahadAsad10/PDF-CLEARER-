# PDF Clearer ✨

A beautiful Streamlit web application that enhances PDF documents for better readability. Features include:

- 🔍 **Zoom/Magnification** - Adjust zoom levels for better visibility
- 🌈 **Contrast Enhancement** - Improve text clarity
- 💡 **Brightness Control** - Adjust brightness levels
- 🌙 **Dark Reading Mode** - Comfortable dark theme for text display
- 🗣️ **Text-to-Speech** - Listen to your documents
- 📄 **PDF Export** - Export enhanced pages as a new PDF

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR\`
   - Or update the path in `pdf_clearer.py` if installed elsewhere

## Usage

Run the Streamlit app:
```bash
streamlit run pdf_clearer.py
```

Or using Python module:
```bash
python -m streamlit run pdf_clearer.py
```

The app will open in your default web browser.

## Features

- Upload any PDF file
- Adjust zoom, contrast, and brightness in the sidebar
- View enhanced pages with improved clarity
- Extract and view text content
- Listen to text using text-to-speech
- Download cleaned PDF with all enhancements

## Technologies

- Streamlit - Web framework
- PyMuPDF (fitz) - PDF processing
- Pillow - Image enhancement
- Tesseract OCR - Text extraction
- pdfplumber - Alternative text extraction
- pyttsx3 - Text-to-speech

## License

MIT

