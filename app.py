import streamlit as st
from azure.storage.blob import BlobServiceClient
import fitz  # PyMuPDF
import io
from PIL import Image

# Azure connection
AZURE_CONNECTION_STRING = st.secrets["AZURE_CONNECTION_STRING"]  # Or hardcode for testing
CONTAINER_NAME = "salesdata"

st.set_page_config(page_title="Azure PDF Viewer", page_icon="📄", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .pdf-header {
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    .stSelectbox label {
        font-weight: bold;
        color: #34495e;
    }
    .footer {
        font-size: 12px;
        text-align: center;
        color: #888;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)


def list_pdfs(_blob_service_client):
    container_client = _blob_service_client.get_container_client(CONTAINER_NAME)
    return [blob.name for blob in container_client.list_blobs() if blob.name.endswith('.pdf')]


def fetch_pdf(_blob_service_client, blob_name):
    blob_client = _blob_service_client.get_blob_client(CONTAINER_NAME, blob_name)
    pdf_bytes = blob_client.download_blob().readall()
    return io.BytesIO(pdf_bytes)

def display_pdf_pages(pdf_stream):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.image(img, caption=f"Page {page_num+1}", use_container_width=True)

# Main app
def main():
    st.sidebar.image("https://assets.zenn.com/strapi_assets/ai_logo_generator_logo_60fd086926.png", use_container_width=True)
    st.sidebar.title("Executive Nexus")
    st.sidebar.markdown("A Gen AI-Powered Cloud Reporting Engine For Strategic Executive Decision-Making")
    
    st.markdown("<div class='pdf-header'>Executive Nexus</div>", unsafe_allow_html=True)


    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        pdf_files = list_pdfs(blob_service_client)

        if not pdf_files:
            st.warning("⚠️ No PDF files found.")
            return

        col1, col2 = st.columns([1, 4])
        with col1:
            selected_pdf = st.selectbox("Choose a PDF to display", pdf_files)

        with col2:
            if selected_pdf:
                st.info(f"Now displaying: **{selected_pdf}**")
                pdf_stream = fetch_pdf(blob_service_client, selected_pdf)
                display_pdf_pages(pdf_stream)


    except Exception as e:
        st.error("🚨 An error occurred while accessing Azure Blob Storage.")
        st.exception(e)

if __name__ == "__main__":
    main()
