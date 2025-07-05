import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import io

def rotate_if_portrait(page):
    if page.rect.height > page.rect.width:
        page.set_rotation(90)  # roter 90 grader med klokka
    return page

def split_landscape_pdf(file_data, split_percent):
    input_pdf = fitz.open(stream=file_data, filetype="pdf")
    output_pdf = fitz.open()

    for page in input_pdf:
        # Automatisk roter om det er portrett
        page = rotate_if_portrait(page)
        width = page.rect.width
        height = page.rect.height
        split_x = width * (split_percent / 100)

        # Venstre
        left_rect = fitz.Rect(0, 0, split_x, height)
        left_page = output_pdf.new_page(width=left_rect.width, height=left_rect.height)
        left_page.show_pdf_page(left_page.rect, input_pdf, page.number, clip=left_rect)

        # Høyre
        right_rect = fitz.Rect(split_x, 0, width, height)
        right_page = output_pdf.new_page(width=right_rect.width, height=right_rect.height)
        right_page.show_pdf_page(right_page.rect, input_pdf, page.number, clip=right_rect)

    return output_pdf.write()

def generate_preview(file_data, split_percent):
    doc = fitz.open(stream=file_data, filetype="pdf")
    page = rotate_if_portrait(doc[0])
    width = page.rect.width
    split_x = int(width * (split_percent / 100))

    pix = page.get_pixmap(dpi=150)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    draw = ImageDraw.Draw(img)
    draw.line([(split_x, 0), (split_x, img.height)], fill="red", width=3)

    return img

# --- Streamlit UI ---
st.set_page_config(page_title="PDF-splitter", layout="centered")
st.title("🖨️ Splitte dobbeltsider i PDF")

uploaded_file = st.file_uploader("Last opp en PDF med dobbeltsider (landskap eller portrett)", type=["pdf"])

split_percent = st.slider(
    "Velg hvor mange prosent fra venstre siden skal splittes:",
    min_value=30,
    max_value=70,
    value=50,
    step=1,
    help="Standard er 50 %, altså midt på siden."
)

if uploaded_file:
    file_bytes = uploaded_file.read()

    st.subheader("🔍 Forhåndsvisning av første side")
    try:
        preview_img = generate_preview(file_bytes, split_percent)
        st.image(preview_img, caption="Rød strek viser hvor siden blir delt", use_column_width=True)
    except Exception as e:
        st.error(f"Klarte ikke å vise forhåndsvisning: {e}")

    if st.button("🚀 Kjør splitting og generer PDF"):
        with st.spinner("Behandler PDF..."):
            result_pdf = split_landscape_pdf(file_bytes, split_percent)

        st.success("✅ Ferdig!")
        st.download_button(
            label="📥 Last ned PDF med splitta sider",
            data=result_pdf,
            file_name="splittet.pdf",
            mime="application/pdf"
        )
