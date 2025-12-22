import streamlit as st
import os
import json
from streamlit_quill import st_quill
from jain_digitizer.common.translator import Translator
from jain_digitizer.common.constants import DEFAULT_PROMPT
from jain_digitizer.common.logger_setup import logger

# --- Page Config ---
st.set_page_config(
    page_title="Jain Digitizer",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #3498db;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .settings-card {
        padding: 2rem;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #eee;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = DEFAULT_PROMPT
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Main Window"

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'>📖 Jain Digitizer</div>", unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        ["Main Window", "Settings"],
        index=0 if st.session_state.current_page == "Main Window" else 1,
        key="nav_radio"
    )
    st.session_state.current_page = page
    
    st.markdown("---")
    st.info("System Status: Online 🟢")

# --- Cached Proxy Functions ---
@st.cache_data(show_spinner=False)
def get_translation_proxy(api_key, system_prompt, files_data):
    """
    Proxy function to call the translator with caching.
    The cache keys are based on the api_key, system_prompt, and the actual file data.
    """
    translator = Translator(api_key, system_prompt)
    return translator.translate_bytes(files_data)

# --- Define Pages ---

def show_main_page():
    st.title("📖 Jain Digitizer")
    st.markdown("High-fidelity OCR and translation for Jain and Hindi literature using **Gemini 2.0 Flash**.")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📤 Upload Files")
        uploaded_files = st.file_uploader(
            "Drop images or PDF files here", 
            type=["png", "jpg", "jpeg", "pdf"], 
            accept_multiple_files=True
        )
        
        if st.button("🚀 Process Files") and uploaded_files:
            if not st.session_state.api_key:
                st.error("Please enter your Gemini API Key in the Settings page.")
            else:
                try:
                    files_data = []
                    for uploaded_file in uploaded_files:
                        bytes_data = uploaded_file.getvalue()
                        mime_type = uploaded_file.type
                        files_data.append((bytes_data, uploaded_file.name, mime_type))
                    
                    with st.spinner(f"Digitizing {len(uploaded_files)} files..."):
                        results = get_translation_proxy(st.session_state.api_key, st.session_state.system_prompt, files_data)
                        st.session_state.results = results
                        st.success("Processing Complete!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.exception("Streamlit process error")

    with col2:
        st.subheader("📄 Preview")
        if uploaded_files:
            for f in uploaded_files:
                st.text(f"✅ {f.name}")
        else:
            st.info("No files uploaded yet. Add some images or a PDF to begin.")

    st.markdown("---")

    # --- Results Section ---
    if st.session_state.results:
        st.markdown("---")
        st.subheader("🎉 Resulting Digitization")
        
        # Concatenate results
        hindi_parts = []
        english_parts = []
        
        for idx, res in enumerate(st.session_state.results):
            fname = res.get('filename', f'File {idx+1}')
            
            # Process Hindi
            h_html = res.get("hindi_ocr", "No OCR text found.")
            # If it's already markdown, convert it. If not, markdown() still works fine on plain text.
            # h_html = markdown.markdown(h_text, extensions=['extra'])
            # hindi_parts.append(f"<h3>📄 {fname}</h3>{h_html}")
            hindi_parts.append(f"<div>{h_html}</div>")
            
            # Process English
            e_html = res.get("english_translation", "No translation found.")
            # e_html = markdown.markdown(e_text, extensions=['extra'])
            english_parts.append(f"<div>{e_html}</div>")
        
        full_hindi_content = "<hr/>".join(hindi_parts)
        full_english_content = "<hr/>".join(english_parts)
        
        col_hindi, col_english = st.columns(2, gap="medium")
        
        with col_hindi:
            st.markdown("#### 🇮🇳 Hindi (Devanagari)")
            
            edited_hindi_html = st_quill(
                value=full_hindi_content,
                key="quill_hindi_main",
                toolbar=[
                    ['bold', 'italic', 'underline', 'strike'],
                    [{'header': 1}, {'header': 2}, {'header': 3}],
                    [{'list': 'ordered'}, {'list': 'bullet'}],
                    ['clean']
                ]
            )
            
            st.download_button(
                label="📥 Download Hindi (.doc)",
                data=f"<html><head><meta charset='utf-8'></head><body>{edited_hindi_html}</body></html>",
                file_name="hindi_ocr.doc",
                mime="application/msword",
                key="dl_hindi"
            )
            
        with col_english:
            st.markdown("#### 🇬🇧 English Translation")
            
            edited_english_html = st_quill(
                value=full_english_content,
                key="quill_english_main",
                toolbar=[
                    ['bold', 'italic', 'underline', 'strike'],
                    [{'header': 1}, {'header': 2}, {'header': 3}],
                    [{'list': 'ordered'}, {'list': 'bullet'}],
                    ['clean']
                ]
            )
            
            st.download_button(
                label="📥 Download English (.doc)",
                data=f"<html><head><meta charset='utf-8'></head><body>{edited_english_html}</body></html>",
                file_name="english_translation.doc",
                mime="application/msword",
                key="dl_english"
            )
        
        if st.button("🗑️ Clear All Results"):
            st.session_state.results = []
            st.rerun()

def show_settings_page():
    st.title("⚙️ Application Settings")
    st.markdown("Configure your AI connection and digitization behavior.")

    with st.container():
        st.markdown("<div class='settings-card'>", unsafe_allow_html=True)
        st.subheader("🔑 API Configuration")
        st.session_state.api_key = st.text_input(
            "Gemini API Key", 
            value=st.session_state.api_key, 
            type="password",
            help="Get your key from https://aistudio.google.com/ and ensure it has access to Gemini 2.0 Flash."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='settings-card'>", unsafe_allow_html=True)
        st.subheader("📝 System Prompt")
        st.info("The prompt below defines how Gemini interprets the manuscript and formats the output. Changes take effect on the next processing run.")
        
        # Use columns for Editor and Markdown Preview
        col_edit, col_prev = st.columns(2, gap="medium")
        
        with col_edit:
            st.markdown("#### ✍️ Markdown Editor")
            new_prompt = st.text_area(
                "System Instructions",
                value=st.session_state.system_prompt,
                height=400,
                help="Enter the raw Markdown instructions for the AI.",
                key="markdown_editor"
            )
            
            if new_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = new_prompt
                st.success("Prompt updated!")

        with col_prev:
            st.markdown("#### 👁️ Rendered Preview")
            st.markdown(st.session_state.system_prompt)

        if st.button("♻️ Reset to Default Prompt"):
            st.session_state.system_prompt = DEFAULT_PROMPT
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- Page Routing ---
if st.session_state.current_page == "Main Window":
    show_main_page()
else:
    show_settings_page()

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini 2.0 Flash • Built with Streamlit & Quill")
