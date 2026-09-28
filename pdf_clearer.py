import io
import os
from datetime import datetime

import fitz
import pdfplumber
import pytesseract
import streamlit as st
from PIL import Image, ImageEnhance

st.set_page_config(
    page_title="PDF Clearer",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
}
[data-testid="stSidebar"] {
    background: rgba(15, 32, 47, 0.96);
}
.block-container { padding: 2rem 3rem 3rem; max-width: 1400px; }
.hero {
    text-align: center; padding: 1rem 0 1.5rem;
}
.hero h1 { color: #a8e6ff; margin-bottom: .35rem; }
.hero p { color: #d9faff; font-size: 1.05rem; }
.card {
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 16px;
    padding: 1rem 1.2rem;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>📘 PDF Clearer</h1>
  <p>Make difficult PDFs easier to read, search, listen to, and export.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("⚙️ Enhancement Settings")
zoom_level = st.sidebar.slider("🔍 Zoom / Magnification", 1.0, 3.0, 1.5, 0.1)
contrast_level = st.sidebar.slider("🌈 Contrast", 1.0, 3.0, 1.5, 0.1)
brightness_level = st.sidebar.slider("💡 Brightness", 0.5, 2.0, 1.0, 0.1)
dark_mode = st.sidebar.toggle("🌙 Dark Reading Mode")
ocr_enabled = st.sidebar.toggle("🔎 OCR Text Extraction", True)
tts_enabled = st.sidebar.toggle("🗣️ Text-to-Speech")
export_enabled = st.sidebar.toggle("📄 Enable Clean PDF Export", True)

st.sidebar.divider()
st.sidebar.caption("Tip: For scanned PDFs, enable OCR. For normal digital PDFs, direct text extraction is faster.")

uploaded_file = st.file_uploader("📂 Upload a PDF", type=["pdf"])

def enhance_page(page, zoom, contrast, brightness):
    pix = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        alpha=False,
        colorspace=fitz.csRGB,
    )
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    return image

def extract_text_direct(file_bytes):
    parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n\n".join(parts).strip()

def configure_tesseract():
    configured = os.getenv("TESSERACT_CMD")
    if configured and os.path.isfile(configured):
        pytesseract.pytesseract.tesseract_cmd = configured
        return True

    discovered = [
        r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    for path in discovered:
        if os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

@st.cache_data(show_spinner=False, max_entries=3)
def process_pdf(file_bytes, zoom, contrast, brightness, use_ocr):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    images = []
    ocr_text = []
    direct_text = extract_text_direct(file_bytes)

    for page in doc:
        image = enhance_page(page, zoom, contrast, brightness)
        images.append(image)
        if use_ocr:
            ocr_text.append(pytesseract.image_to_string(image))

    doc.close()

    if use_ocr and any(text.strip() for text in ocr_text):
        text = "\n\n".join(ocr_text).strip()
    else:
        text = direct_text

    return images, text

def build_clean_pdf(images):
    output = fitz.open()
    for image in images:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        page = output.new_page(width=image.width, height=image.height)
        page.insert_image(page.rect, stream=buffer.getvalue())
    data = output.tobytes(garbage=4, deflate=True)
    output.close()
    return data

if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    file_size_mb = len(file_bytes) / (1024 * 1024)

    st.success(f"✅ {uploaded_file.name} uploaded • {file_size_mb:.2f} MB")

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_count = len(doc)
    doc.close()

    c1, c2, c3 = st.columns(3)
    c1.metric("Pages", page_count)
    c2.metric("File size", f"{file_size_mb:.2f} MB")
    c3.metric("OCR", "On" if ocr_enabled else "Off")

    if ocr_enabled and not configure_tesseract():
        st.warning(
            "OCR is enabled, but Tesseract was not found. "
            "Install Tesseract or set the TESSERACT_CMD environment variable. "
            "The app will still use regular PDF text extraction."
        )
        use_ocr = False
    else:
        use_ocr = ocr_enabled

    with st.spinner("Enhancing your PDF…"):
        images, all_text = process_pdf(
            file_bytes,
            zoom_level,
            contrast_level,
            brightness_level,
            use_ocr,
        )

    st.success("✨ PDF processed successfully!")

    st.subheader("📄 Enhanced Preview")
    preview_page = st.number_input(
        "Preview page",
        min_value=1,
        max_value=len(images),
        value=1,
        step=1,
    )
    st.image(
        images[preview_page - 1],
        caption=f"Enhanced Page {preview_page} of {len(images)}",
        use_container_width=True,
    )

    st.subheader("📝 Extracted Text")
    if dark_mode:
        st.markdown(
            f'<div class="card"><pre style="white-space:pre-wrap;color:#e6faff;">'
            f'{all_text or "No text could be extracted."}</pre></div>',
            unsafe_allow_html=True,
        )
    else:
        st.text_area(
            "Document text",
            all_text or "No text could be extracted.",
            height=350,
            label_visibility="collapsed",
        )

    col1, col2 = st.columns(2)

    with col1:
        if tts_enabled:
            st.subheader("🔊 Text-to-Speech")
            st.info(
                "Text-to-speech uses the local system speech engine. "
                "It works best when running the app locally."
            )
            if st.button("▶️ Read document aloud", use_container_width=True):
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(all_text)
                    engine.runAndWait()
                    st.success("Speech playback complete.")
                except Exception as exc:
                    st.error(f"Text-to-speech is unavailable: {exc}")

    with col2:
        if export_enabled:
            st.subheader("📥 Export")
            cleaned_pdf = build_clean_pdf(images)
            export_name = f"cleaned_{os.path.splitext(uploaded_file.name)[0]}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
            st.download_button(
                "📥 Download Cleaned PDF",
                data=cleaned_pdf,
                file_name=export_name,
                mime="application/pdf",
                use_container_width=True,
            )

else:
    st.info("📄 Upload a PDF to get started.")
    st.markdown("""
    <div class="card">
    <h3>What you can do</h3>
    <p>✨ Improve contrast and brightness &nbsp; • &nbsp; 🔎 Extract text with OCR<br>
    🌙 Use a dark reading mode &nbsp; • &nbsp; 🔊 Listen to extracted text<br>
    📥 Export an enhanced copy of your document</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown(
    "<div style='text-align:center;color:#8fd3f4;'>"
    "Built with ❤️ using Python, Streamlit, PyMuPDF, Pillow & Tesseract OCR"
    "</div>",
    unsafe_allow_html=True,
)
