import streamlit as st
import fitz  # PyMuPDF
import io

def split_landscape_pdf(file_data):
    input_pdf = fitz.open(stream=file_data, filetype="pdf")
    output_pdf = fitz.open()

    for page in input_pdf:
        width = page.rect.width
        height = page.rect.height

        # Venstre halvdel
        left_rect = fitz.Rect(0, 0, width / 2, height)
        left_page = output_pdf.new_page(width=left_rect.width, height=left_rect.height)
        left_page.show_pdf_page(left_page.rect, input_pdf, page.number, clip=left_rect)

        # Høyre halvdel
        right_rect = fitz.Rect(width / 2, 0, width, height)
        right_page = output_pdf.new_page(width=right_rect.width, height=right_rect.height)
        right_page.show_pdf_page(right_page.rect, input_pdf, page.number, clip=right_rect)

    # Lagre til bytes
    output_bytes = output_pdf.write()
    return output_bytes

# --- Streamlit UI ---
st.set_page_config(page_title="PDF-splitter", layout="centered")
st.title("🖨️ Splitte dobbeltsider i PDF")

uploaded_file = st.file_uploader("Last opp en PDF med dobbeltsider (landskap)", type=["pdf"])

if uploaded_file:
    with st.spinner("Behandler PDF..."):
        result_pdf = split_landscape_pdf(uploaded_file.read())

    st.success("✅ Ferdig!")
    st.download_button(
        label="📥 Last ned PDF med splitta sider",
        data=result_pdf,
        file_name="splittet.pdf",
        mime="application/pdf"
    )
