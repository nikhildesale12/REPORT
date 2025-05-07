import streamlit as st
from azure.storage.blob import BlobServiceClient
import fitz  # PyMuPDF
import io
from PIL import Image

# Azure connection
AZURE_CONNECTION_STRING = st.secrets["AZURE_CONNECTION_STRING"]
CONTAINER_NAME = "salesdata"

# --- Page Configuration ---
st.set_page_config(page_title="Executive Nexus Viewer", page_icon="📄", layout="wide")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    html, body, .main {
        background-color: #f4f6f9;
    }
    .pdf-header h1 {
        font-size: 36px;
        background: linear-gradient(90deg, #0052cc, #00b8d9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
    }
    .stSelectbox label {
        font-weight: bold;
        color: #0a1f44;
    }
    .stImage {
        border-radius: 8px;
        box-shadow: 0px 0px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .info-banner {
        padding: 10px;
        background-color: #e6f4ff;
        border-left: 6px solid #1a73e8;
        margin-top: 10px;
        border-radius: 4px;
    }
    .footer {
        text-align: center;
        font-size: 13px;
        color: #aaa;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Azure Blob Helpers ---
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
        st.image(img, caption=f"📄 Page {page_num + 1}", use_container_width=True)

# --- Main Application ---
def main():
    st.sidebar.image("https://assets.zenn.com/strapi_assets/ai_logo_generator_logo_60fd086926.png", use_container_width=True)
    st.sidebar.markdown(
    "<h2 style='color:#0052cc; font-weight:700;'>Executive Nexus</h2>",
    unsafe_allow_html=True
)
    st.sidebar.markdown(
        """
        <small>A Gen AI-Powered Cloud Reporting Engine<br>
        For Strategic Executive Decision-Making</small>
        """, unsafe_allow_html=True
    )

    st.markdown("<div class='pdf-header'><h1> Executive Nexus Report Viewer</h1></div>", unsafe_allow_html=True)

    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        pdf_files = list_pdfs(blob_service_client)

        if not pdf_files:
            st.warning("⚠️ No PDF reports found in the container.")
            return

        col1, col2 = st.columns([1, 5])
        with col1:
            selected_pdf = st.selectbox("Choose a report", pdf_files)

        with col2:
            if selected_pdf:
                pdf_stream = fetch_pdf(blob_service_client, selected_pdf)
                display_pdf_pages(pdf_stream)

    except Exception as e:
        st.error("🚨 An error occurred while accessing Azure Blob Storage.")
        st.exception(e)

    st.markdown("<div class='footer'>© 2025 Executive Nexus – Powered by Azure + Gen AI</div>", unsafe_allow_html=True)

# --- Run App ---
if __name__ == "__main__":
    main()
