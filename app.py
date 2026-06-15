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
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Swiss Minimalist / Neo-Brutalist CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap');
    
    /* Global Overrides */
    .stApp {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #FFFFFF;
    }

    /* Remove standard Streamlit padding */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Architectural Header */
    .header-container {
        border-bottom: 2px solid #000000;
        margin-bottom: 3rem;
        padding-bottom: 1rem;
    }

    h1 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: -0.05em !important;
        color: #000000 !important;
        font-size: 4.5rem !important;
        line-height: 0.9 !important;
        margin: 0 !important;
    }

    .tagline {
        font-size: 1.2rem;
        font-weight: 400;
        color: #000000;
        margin-top: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Brutalist Buttons */
    .stButton > button {
        border-radius: 0px !important;
        border: 2px solid #000000 !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        padding: 1rem 2rem !important;
        transition: all 0.1s ease !important;
    }

    .stButton > button:hover {
        background-color: #FF4B2B !important; /* Safety Orange */
        border-color: #FF4B2B !important;
        color: #FFFFFF !important;
        transform: translate(-2px, -2px);
        box-shadow: 4px 4px 0px #000000;
    }

    .stButton > button:active {
        transform: translate(0px, 0px);
        box-shadow: 0px 0px 0px #000000;
    }

    /* Form Elements */
    .stTextArea textarea {
        border-radius: 0px !important;
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.1rem !important;
        color: #000000 !important;
    }

    /* Metrics / Data Displays */
    [data-testid="stMetric"] {
        border: 2px solid #000000;
        border-radius: 0px;
        padding: 1.5rem;
        background-color: #F3F4F6;
    }

    [data-testid="stMetricLabel"] {
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #000000 !important;
    }

    /* Result Containers */
    .stExpander {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        background-color: #FFFFFF !important;
        margin-bottom: 1rem !important;
    }

    /* Sidebar Branding */
    .sidebar-brand {
        font-weight: 700;
        font-size: 1.5rem;
        text-transform: uppercase;
        letter-spacing: -0.02em;
        border-bottom: 2px solid #000000;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border: 2px solid #000000;
        padding: 0px;
    }

    .stTabs [data-baseweb="tab"] {
        border-right: 2px solid #000000 !important;
        border-radius: 0px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #000000 !important;
        color: #FFFFFF !important;
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
    st.markdown('<div class="sidebar-brand">SUMMARIZER.AI</div>', unsafe_allow_html=True)
    
    choice = st.selectbox("INDEX", ["01_HOME", "02_ANALYTICS", "03_ABOUT"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("**CONFIG**")
    method = st.radio("ALGORITHM", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("DEPTH", 1, 10, 3)
    
    st.markdown("---")
    st.caption("ENGINE_REF: TEYZIX_V3.0")

# --- Main Logic ---
if "01_HOME" in choice:
    # Header Section
    st.markdown('<div class="header-container"><h1>EXTRACT<br>THE CORE.</h1><p class="tagline">Architectural Document Distillation</p></div>', unsafe_allow_html=True)

    # Input Section
    tab1, tab2, tab3 = st.tabs(["01_TEXT", "02_FILE", "03_BATCH"])
    
    documents_input = []
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        text_data = st.text_area("INPUT_SOURCE", height=300, placeholder="INSERT TEXT DATA...", label_visibility="collapsed")
        if text_data.strip():
            documents_input = [("PASTED_DATA", text_data)]
            
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        file = st.file_uploader("UPLOAD_FILE", type=["txt", "pdf"], label_visibility="collapsed")
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
                    
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        files = st.file_uploader("UPLOAD_BATCH", type=["txt", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
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
    if st.button("RUN_SUMMARIZATION", use_container_width=True):
        if not documents_input:
            st.warning("NO_INPUT_DETECTED")
        else:
            with st.spinner("DISTILLING..."):
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
            with st.expander(f"FILE: {doc['name'].upper()}", expanded=True):
                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    st.markdown("**ORIGINAL_SOURCE**")
                    st.markdown(f'<div style="border: 1px solid #000; padding: 1rem; background: #f9f9f9; font-size: 0.9rem;">{doc["original"][:1200]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("**DISTILLED_CORE**")
                    st.markdown(f'<div style="border: 1px solid #000; padding: 1rem; background: #FF4B2B; color: #FFF; font-weight: 500;">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                # Export
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                a1.download_button("EXPORT_TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_CORE.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("EXPORT_PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_CORE.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif "02_ANALYTICS" in choice:
    st.markdown('<div class="header-container"><h1>DATA<br>METRICS.</h1><p class="tagline">Quantitative Document Analysis</p></div>', unsafe_allow_html=True)
    
    docs = st.session_state.get('documents', [])
    if not docs:
        st.warning("NO_DATA_AVAILABLE. RUN_HOME_FIRST.")
    else:
        selected = st.selectbox("SELECT_FILE", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        m1.metric("SENTENCES", stats['num_sentences'])
        m2.metric("WORD_COUNT", stats['num_words'])
        m3.metric("TOP_KEYWORD", stats['keywords'][0].upper() if stats['keywords'] else "N/A")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### FREQUENCY_CHART")
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'), color="#000000")

else:
    st.markdown('<div class="header-container"><h1>ABOUT<br>SYSTEM.</h1><p class="tagline">Technical Specifications</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### PHILOSOPHY
    SUMMARIZER.AI IS A PROFESSIONAL-GRADE DISTILLATION ENGINE. WE PRIORITIZE CLARITY, PRECISION, AND STRUCTURAL INTEGRITY. NO FLUFF. JUST THE CORE.
    
    ### ARCHITECTURE
    - **MODEL:** NLTK TOKENIZATION + TF-IDF WEIGHTING
    - **UI:** SWISS MINIMALIST GRID SYSTEM
    - **TYPE:** SPACE GROTESK GEOMETRIC
    - **ACCENT:** SAFETY ORANGE (#FF4B2B)
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("SYSTEM_STATUS: OPERATIONAL • V3.0")
