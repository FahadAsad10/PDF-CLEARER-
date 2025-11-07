import fitz  # PyMuPDF
import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract

# Ensure pytesseract knows where the Tesseract OCR binary is installed (Windows default path).
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
import io
import pdfplumber
import pyttsx3
from datetime import datetime

# -------------------------------
# PDF CLEARER ✨ — v2 (Styled)
# -------------------------------

st.set_page_config(
    page_title="PDF Clearer ✨",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
/* Global styles */
body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #FFFFFF;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
[data-testid="stSidebar"] {
    background-color: rgba(15, 32, 47, 0.9);
    color: white;
}
.sidebar .sidebar-content {
    background-color: rgba(15, 32, 47, 0.9);
}
h1, h2, h3, h4, h5, h6 {
    color: #a8e6ff;
}
.block-container {
    padding: 2rem 3rem;
}
.stButton button {
    background: linear-gradient(90deg, #56CCF2, #2F80ED);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    cursor: pointer;
    transition: 0.3s;
}
.stButton button:hover {
    background: linear-gradient(90deg, #2F80ED, #56CCF2);
    transform: scale(1.03);
}
.stDownloadButton button {
    background: linear-gradient(90deg, #11998e, #38ef7d);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}
.stDownloadButton button:hover {
    background: linear-gradient(90deg, #38ef7d, #11998e);
    transform: scale(1.03);
}
div[data-testid="stMarkdownContainer"] pre {
    background-color: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 10px;
    color: #f2f2f2;
    overflow-x: auto;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Title & Intro ---
st.markdown("<h1 style='text-align:center;'>📘 PDF Clearer — Make Any PDF Easier to Read</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#d9faff; font-size:1.1rem; margin-bottom:20px;">
Enhance clarity, extract text, improve contrast, and even listen to your documents.
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
zoom_level = st.sidebar.slider("🔍 Zoom / Magnification", 1.0, 3.0, 1.5, 0.1)
contrast_level = st.sidebar.slider("🌈 Contrast Enhancement", 1.0, 3.0, 1.5, 0.1)
brightness_level = st.sidebar.slider("💡 Brightness", 0.5, 2.0, 1.0, 0.1)
dark_mode = st.sidebar.toggle("🌙 Dark Reading Mode")
tts_enabled = st.sidebar.toggle("🗣️ Text-to-Speech")
export_pdf = st.sidebar.toggle("📄 Export as new cleaned PDF")

uploaded_file = st.file_uploader("📂 Upload your PDF", type=["pdf"])

# --- Processing Logic ---
if uploaded_file:
    st.success("✅ File uploaded successfully!")
    file_bytes = uploaded_file.read()
    pdf_stream = io.BytesIO(file_bytes)

    with st.spinner("Processing your PDF... please wait ⏳"):
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        all_text = ""
        cleaned_pages = []

        for page_num, page in enumerate(doc, start=1):
            st.markdown(f"<h3>📄 Page {page_num}</h3>", unsafe_allow_html=True)

            # Render page to image with magnification
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_level, zoom_level))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Apply image enhancements
            img = ImageEnhance.Contrast(img).enhance(contrast_level)
            img = ImageEnhance.Brightness(img).enhance(brightness_level)

            # OCR extraction
            extracted_text = pytesseract.image_to_string(img)
            if not extracted_text.strip():
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    extracted_text = pdf.pages[page_num - 1].extract_text() or ""

            all_text += extracted_text + "\n\n"
            cleaned_pages.append(img)

            # Display enhanced preview
            st.image(img, caption=f"Enhanced Page {page_num}", use_container_width=True)

        st.success("✨ PDF processed successfully!")

    # --- Display Text ---
    if dark_mode:
        st.markdown(
            f"<div style='background-color:rgba(255,255,255,0.05); "
            f"color:#e6faff; padding:20px; border-radius:10px;'>"
            f"<h3>🌓 Cleaned Text (Dark Mode)</h3><pre>{all_text}</pre></div>",
            unsafe_allow_html=True,
        )
    else:
        st.text_area("📝 Cleaned Text", all_text, height=400)

    # --- Text to Speech ---
    if tts_enabled:
        st.markdown("### 🔊 Text-to-Speech Output")
        if st.button("▶️ Play Audio"):
            engine = pyttsx3.init()
            engine.say(all_text)
            engine.runAndWait()
            st.success("✅ Speech playback complete!")

    # --- Export as PDF ---
    if export_pdf:
        export_name = f"cleaned_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_pdf = fitz.open()

        for img in cleaned_pages:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            img_doc = fitz.open(stream=img_bytes, filetype="png")
            rect = img_doc[0].rect
            pdf_bytes = fitz.open()
            page = pdf_bytes.new_page(width=rect.width, height=rect.height)
            page.insert_image(rect, stream=img_bytes.getvalue())
            output_pdf.insert_pdf(pdf_bytes)

        output_bytes = output_pdf.write()
        st.download_button(
            label="📥 Download Cleaned PDF",
            data=output_bytes,
            file_name=export_name,
            mime="application/pdf",
        )

else:
    st.info("📄 Upload a PDF to get started!")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center; color:#8fd3f4; font-size:0.9rem;'>"
    "Created with ❤️ using Streamlit, PyMuPDF, Pillow & Tesseract OCR"
    "</div>",
    unsafe_allow_html=True,
)
