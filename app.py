import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import mimetypes # determines file types, extensions
import fitz  # for reading PDF files
import pandas as pd
from docx import Document
from io import BytesIO  # Import BytesIO for handling file-like objects

# Set page config to improve layout
st.set_page_config(page_title="Word Cloud Generator", page_icon="bookmark_tabs")

# Add a header with a custom style
st.markdown("<h1 style='text-align: center; color: #4B0082;'>Generate Word Cloud</h1>", unsafe_allow_html=True)

# explanatory text for user
st.markdown("""
    <h3 style='text-align: center; color: #696969;'>Create beautiful word clouds from your text or uploaded files!</h3>
    <p style='text-align: center; font-size: 16px; color: #708090;'>Upload a .txt, .pdf, .docx, or .xlsx file, or enter your text below.</p>
""", unsafe_allow_html=True)

def read_file(uploaded_file):
    mime_type, _ = mimetypes.guess_type(uploaded_file.name)

    # Read txt file
    if mime_type == 'text/plain':
        content = uploaded_file.read().decode('utf-8')
        return content
    # Read PDF file
    elif mime_type == 'application/pdf':
        content = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_document:
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                content += page.get_text() + "\n"
        return content
    # Read Document File
    elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc = Document(uploaded_file)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    # Read Excel file
    elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        data_frame = pd.read_excel(uploaded_file)
        content = data_frame.to_string()
        return content
    # Handle unsupported format file
    else:
        return "Unsupported file type."

# Generate Word Cloud
def create_word_cloud(text):
    word_cloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return word_cloud

# Session state to manage text and file input modes
if "mode" not in st.session_state:
    st.session_state.mode = "Text"
if "text_cloud" not in st.session_state:
    st.session_state.text_cloud = None
if "file_cloud" not in st.session_state:
    st.session_state.file_cloud = None

# Switch between text and file modes
def switch_to_text():
    st.session_state.mode = "Text"
    st.session_state.file_cloud = None
def switch_to_file():
    st.session_state.mode = "File"
    st.session_state.text_cloud = None

# Checkboxes to switch between modes, text and file
col1, col2 = st.columns(2)
with col1:
    text_mode = st.checkbox("Text Input", value=st.session_state.mode == "Text", key="text_mode", on_change=switch_to_text)
with col2:
    file_mode = st.checkbox("File Upload", value=st.session_state.mode == "File", key="file_mode", on_change=switch_to_file)

# Mutual exclusivity of checkboxes(only one can execute at a time)
if text_mode and st.session_state.mode != "Text":
    switch_to_text()
elif file_mode and st.session_state.mode != "File":
    switch_to_file()

# Text Input Mode
if st.session_state.mode == "Text":
    input_text = st.text_area("Enter Text", "", height=100)
    if st.button("Text To Cloud", key="text_cloud_button"):
        if input_text:
            st.session_state.text_cloud = create_word_cloud(input_text)
        else:
            st.error("Please enter some text.")

    if st.session_state.text_cloud:
        plt.figure(figsize=(10, 4))
        plt.imshow(st.session_state.text_cloud, interpolation='bilinear')
        plt.axis('off')
        st.header("Generated Word Cloud")
        st.pyplot(plt)

        img_bytes = BytesIO()
        st.session_state.text_cloud.to_image().save(img_bytes, format='PNG')
        img_bytes.seek(0)
        st.download_button("Download Word Cloud Image", img_bytes, "word_cloud.png", "image/png")

# File Upload Mode
elif st.session_state.mode == "File":
    input_file = st.file_uploader("Upload file to generate word cloud!", type=["txt", "pdf", "docx", "xlsx"])
    if st.button("File To Cloud", key="file_cloud_button"):
        if input_file:
            text = read_file(input_file)
            if text:
                st.session_state.file_cloud = create_word_cloud(text)
            else:
                st.error("The uploaded file is empty or not readable.")
        else:
            st.error("Please upload a file.")

    if st.session_state.file_cloud:
        plt.figure(figsize=(10, 4))
        plt.imshow(st.session_state.file_cloud, interpolation='bilinear')
        plt.axis('off')
        st.header("Generated Word Cloud")
        st.pyplot(plt)

        img_bytes = BytesIO()
        st.session_state.file_cloud.to_image().save(img_bytes, format='PNG')
        img_bytes.seek(0)
        st.download_button("Download Word Cloud Image", img_bytes, "word_cloud.png", "image/png")

# Footer Line
st.markdown("---")
