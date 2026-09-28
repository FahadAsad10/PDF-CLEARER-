import io
import os
from datetime import datetime

import fitz
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
.hero { text-align: center; padding: 1rem 0 1.5rem; }
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
st.sidebar.caption(
    "Tip: Digital PDFs use fast text extraction. OCR is only used for pages "
    "that do not contain selectable text."
)

uploaded_file = st.file_uploader("📂 Upload a PDF", type=["pdf"])


def enhance_page(page, zoom, contrast, brightness):
    pix = page.get_pixmap(
        matrix=fitz.Matrix(zoom, zoom),
        alpha=False,
        colorspace=fitz.csRGB,
    )
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    return image


def configure_tesseract():
    configured = os.getenv("TESSERACT_CMD")
    if configured and os.path.isfile(configured):
        pytesseract.pytesseract.tesseract_cmd = configured
        return True

    discovered = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
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
def get_pdf_info(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        page_count = len(doc)
        direct_text = [page.get_text("text").strip() for page in doc]
    return page_count, direct_text


@st.cache_data(show_spinner=False, max_entries=3)
def ocr_missing_pages(file_bytes, missing_pages, zoom, contrast, brightness):
    if not missing_pages:
        return {}

    results = {}
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page_number in missing_pages:
            image = enhance_page(
                doc[page_number],
                zoom,
                contrast,
                brightness,
            )
            results[page_number] = pytesseract.image_to_string(image).strip()
    return results


@st.cache_data(show_spinner=False, max_entries=3)
def render_preview(file_bytes, page_number, zoom, contrast, brightness):
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return enhance_page(doc[page_number], zoom, contrast, brightness)


@st.cache_data(show_spinner=False, max_entries=2)
def build_clean_pdf(file_bytes, zoom, contrast, brightness):
    output = fitz.open()
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as source:
            for page in source:
                image = enhance_page(page, zoom, contrast, brightness)
                buffer = io.BytesIO()
                image.save(buffer, format="PNG", optimize=True)
                new_page = output.new_page(width=image.width, height=image.height)
                new_page.insert_image(new_page.rect, stream=buffer.getvalue())

        return output.tobytes(garbage=4, deflate=True)
    finally:
        output.close()


if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    file_size_mb = len(file_bytes) / (1024 * 1024)

    st.success(f"✅ {uploaded_file.name} uploaded • {file_size_mb:.2f} MB")

    page_count, direct_text = get_pdf_info(file_bytes)

    c1, c2, c3 = st.columns(3)
    c1.metric("Pages", page_count)
    c2.metric("File size", f"{file_size_mb:.2f} MB")
    c3.metric("OCR", "On" if ocr_enabled else "Off")

    all_text_parts = list(direct_text)
    missing_pages = [i for i, text in enumerate(direct_text) if not text.strip()]

    use_ocr = False
    if ocr_enabled and missing_pages:
        if configure_tesseract():
            use_ocr = True
        else:
            st.warning(
                "OCR is enabled, but Tesseract was not found. "
                "Regular PDF text extraction will still be used."
            )

    if use_ocr:
        with st.spinner(f"Running OCR on {len(missing_pages)} scanned page(s)…"):
            ocr_results = ocr_missing_pages(
                file_bytes,
                tuple(missing_pages),
                zoom_level,
                contrast_level,
                brightness_level,
            )
        for page_number, text in ocr_results.items():
            all_text_parts[page_number] = text

    all_text = "\n\n".join(
        text for text in all_text_parts if text.strip()
    ).strip()

    st.success(
        f"✨ PDF processed • {len(missing_pages)} page(s) needed OCR"
        if use_ocr
        else "✨ PDF processed successfully!"
    )

    st.subheader("📄 Enhanced Preview")
    preview_page = st.number_input(
        "Preview page",
        min_value=1,
        max_value=page_count,
        value=1,
        step=1,
    )
    preview_image = render_preview(
        file_bytes,
        preview_page - 1,
        zoom_level,
        contrast_level,
        brightness_level,
    )
    st.image(
        preview_image,
        caption=f"Enhanced Page {preview_page} of {page_count}",
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
            export_name = (
                f"cleaned_{os.path.splitext(uploaded_file.name)[0]}_"
                f"{datetime.now():%Y%m%d_%H%M%S}.pdf"
            )
            if st.button("⚙️ Prepare Cleaned PDF", use_container_width=True):
                with st.spinner("Building cleaned PDF…"):
                    st.session_state["cleaned_pdf"] = build_clean_pdf(
                        file_bytes,
                        zoom_level,
                        contrast_level,
                        brightness_level,
                    )

            cleaned_pdf = st.session_state.get("cleaned_pdf")
            if cleaned_pdf:
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
