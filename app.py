import streamlit as st
import os
import pandas as pd
from summarizer import (
    DocumentSummarizer,
    read_file,
    generate_txt_bytes,
    generate_pdf_bytes,
    generate_combined_txt_bytes,
    generate_pdf_bytes_multi,
)

# --- Page Config ---
st.set_page_config(
    page_title="SUMMARIZER.AI",
    page_icon="□",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Swiss Pastel Minimalist CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #FCFAFF;
    }

    /* Architectural Header */
    .header-container {
        border-bottom: 2px solid #1F2937;
        margin-bottom: 3rem;
        padding-bottom: 1rem;
        background: #F3F0FF; /* Soft Pastel Lavender */
        padding: 2rem;
        border-radius: 0 0 40px 0;
    }

    h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: -0.05em !important;
        color: #1F2937 !important;
        font-size: 4rem !important;
        line-height: 1 !important;
        margin: 0 !important;
    }

    .tagline {
        font-size: 1.1rem;
        font-weight: 500;
        color: #6D28D9;
        margin-top: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }

    /* Pastel Cards */
    .pastel-card-mint {
        background-color: #ECFDF5;
        border: 2px solid #059669;
        padding: 1.5rem;
        border-radius: 20px;
    }

    .pastel-card-lavender {
        background-color: #F5F3FF;
        border: 2px solid #7C3AED;
        padding: 1.5rem;
        border-radius: 20px;
    }

    /* Brutalist Buttons with Pastel Accent */
    .stButton > button {
        border-radius: 12px !important;
        border: 2px solid #1F2937 !important;
        background-color: #1F2937 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        padding: 1rem 2rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button:hover {
        background-color: #DDD6FE !important; /* Pastel Lavender */
        border-color: #1F2937 !important;
        color: #1F2937 !important;
        transform: translate(-4px, -4px);
        box-shadow: 6px 6px 0px #1F2937;
    }

    /* Tabs with Pastel Colors */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #F3F4F6 !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        color: #4B5563 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #DDD6FE !important;
        color: #1F2937 !important;
        border-bottom: 3px solid #7C3AED !important;
    }

    /* Metric Styling */
    [data-testid="stMetric"] {
        background-color: #FEF3C7; /* Pastel Amber */
        border: 2px solid #D97706;
        border-radius: 24px;
        padding: 1.5rem;
    }

    /* Result Expander */
    .stExpander {
        border: 2px solid #E5E7EB !important;
        border-radius: 20px !important;
        background-color: #FFFFFF !important;
        overflow: hidden;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Load Model ---
@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color: #7C3AED; font-weight: 800;'>SUMMARIZER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; font-size: 0.85rem;'>ELEGANT DATA DISTILLATION</p>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.selectbox("WORKSPACE", ["01_HOME", "02_ANALYTICS", "03_ABOUT"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("**CONFIGURATION**")
    method = st.radio("MODEL", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("DEPTH", 1, 10, 3)
    
    st.markdown("---")
    st.caption("ENGINE_REF: TEYZIX_V3.1_PASTEL")

# --- Home Page ---
if "01_HOME" in choice:
    st.markdown('<div class="header-container"><h1>Document Summarization System .</h1><p class="tagline">AI-Powered Document Summarization System </p></div>', unsafe_allow_html=True)

    # Input Area
    with st.container():
        t1, t2, t3 = st.tabs(["01_TEXT", "02_FILE", "03_BATCH"])
        
        documents_input = []
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            text_data = st.text_area("INPUT", height=300, placeholder="INSERT TEXT DATA...", label_visibility="collapsed")
            if text_data.strip():
                documents_input = [("PASTED_DATA", text_data)]
                
        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            file = st.file_uploader("UPLOAD", type=["txt", "pdf"], label_visibility="collapsed")
            if file:
                temp_path = f"temp_{file.name}"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    text_data = read_file(temp_path)
                    documents_input = [(file.name, text_data)]
                except Exception as e:
                    st.error(f"ERR: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
        with t3:
            st.markdown("<br>", unsafe_allow_html=True)
            files = st.file_uploader("BATCH", type=["txt", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
            if files:
                for f in files:
                    temp_path = f"temp_{f.name}"
                    try:
                        with open(temp_path, "wb") as f:
                            f.write(f.getbuffer())
                        text_data = read_file(temp_path)
                        documents_input.append((f.name, text_data))
                    except Exception as e:
                        st.error(f"ERR: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("RUN_DISTILLATION", use_container_width=True):
        if not documents_input:
            st.warning("NO_INPUT_DETECTED")
        else:
            with st.spinner("PROCESSING..."):
                results = []
                for name, text in documents_input:
                    try:
                        res = model.summarize(text, method, num_sent)
                        if res.strip():
                            results.append({"name": name, "original": text, "summary": res})
                    except Exception as e:
                        st.error(f"PROCESS_ERR: {e}")
                
                if results:
                    st.session_state['documents'] = results
                    st.session_state['method'] = method

    # Results Section
    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### OUTPUT_RESULTS")
        
        for doc in st.session_state['documents']:
            with st.expander(f"DOCUMENT: {doc['name'].upper()}", expanded=True):
                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    st.markdown("<p style='font-weight: 700; color: #1F2937;'>ORIGINAL_SOURCE</p>", unsafe_allow_html=True)
                    st.markdown(f'<div style="border: 2px solid #E5E7EB; padding: 1.5rem; background: #F9FAFB; border-radius: 15px; font-size: 0.95rem; line-height: 1.6;">{doc["original"][:1200]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p style='font-weight: 700; color: #7C3AED;'>DISTILLED_CORE</p>", unsafe_allow_html=True)
                    st.markdown(f'<div style="border: 2px solid #7C3AED; padding: 1.5rem; background: #F5F3FF; color: #1F2937; font-weight: 500; border-radius: 15px; line-height: 1.6;">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                # Export
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                a1.download_button("EXPORT_TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_CORE.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("EXPORT_PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_CORE.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif "02_ANALYTICS" in choice:
    st.markdown('<div class="header-container"><h1>DATA<br>METRICS.</h1><p class="tagline">Quantitative Pastel Analysis</p></div>', unsafe_allow_html=True)
    
    docs = st.session_state.get('documents', [])
    if not docs:
        st.warning("NO_DATA_AVAILABLE. RUN_HOME_FIRST.")
    else:
        selected = st.selectbox("SELECT_FILE", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        m1.metric("SENTENCES", stats['num_sentences'])
        m2.metric("WORDS", stats['num_words'])
        m3.metric("KEYWORD", stats['keywords'][0].upper() if stats['keywords'] else "N/A")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### FREQUENCY_CHART")
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'), color="#A78BFA")

else:
    st.markdown('<div class="header-container"><h1>ABOUT<br>SYSTEM.</h1><p class="tagline">Refined Technical Specifications</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### PHILOSOPHY
    SUMMARIZER.AI. WE BELIEVE PROFESSIONAL TOOLS SHOULD BE BOTH POWERFUL AND PLEASANT TO NAVIGATE.
    
    ### ARCHITECTURE
    - **MODEL:** NLTK + TF-IDF
    - **UI:** PASTEL SWISS MINIMALIST
    - **TYPE:** SPACE GROTESK
    - **ACCENTS:** LAVENDER, MINT, AMBER
    """)
    
    st.info("SYSTEM_STATUS: OPERATIONAL ")
