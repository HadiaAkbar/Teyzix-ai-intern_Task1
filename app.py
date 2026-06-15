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

# --- Natural 3D CSS with Organic Design ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #faf9f7 0%, #f5f3f0 50%, #f0ebe5 100%);
        min-height: 100vh;
    }

    /* Natural 3D Header with Depth */
    .header-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(245,240,235,0.5) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        margin-bottom: 3rem;
        padding: 3rem 2.5rem;
        border-radius: 24px;
        box-shadow: 
            0 8px 32px rgba(0,0,0,0.04),
            0 2px 8px rgba(0,0,0,0.02),
            inset 0 1px 0 rgba(255,255,255,0.5);
        position: relative;
        overflow: hidden;
    }

    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .header-container::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(34,197,94,0.06) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    h1 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: #1a1410 !important;
        font-size: 3.5rem !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        position: relative;
        z-index: 1;
        background: linear-gradient(135deg, #1a1410 0%, #3d2817 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .tagline {
        font-size: 0.95rem;
        font-weight: 500;
        color: #7c6b5d;
        margin-top: 1rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }

    /* Natural 3D Cards with Layering */
    .card-3d {
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(248,245,240,0.6) 100%);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.4);
        padding: 1.75rem;
        border-radius: 20px;
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.06),
            0 8px 16px rgba(0,0,0,0.03),
            inset 0 1px 0 rgba(255,255,255,0.6);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        position: relative;
    }

    .card-3d:hover {
        transform: translateY(-8px) translateZ(0);
        box-shadow: 
            0 30px 60px rgba(0,0,0,0.12),
            0 12px 24px rgba(0,0,0,0.06),
            inset 0 1px 0 rgba(255,255,255,0.8);
    }

    .card-accent-green {
        border-color: rgba(34,197,94,0.2);
        background: linear-gradient(135deg, rgba(240,253,244,0.6) 0%, rgba(220,252,231,0.4) 100%);
    }

    .card-accent-purple {
        border-color: rgba(139,92,246,0.2);
        background: linear-gradient(135deg, rgba(245,240,255,0.6) 0%, rgba(232,218,255,0.4) 100%);
    }

    .card-accent-amber {
        border-color: rgba(217,119,6,0.2);
        background: linear-gradient(135deg, rgba(254,252,232,0.6) 0%, rgba(253,230,138,0.3) 100%);
    }

    /* Natural 3D Buttons */
    .stButton > button {
        border-radius: 14px !important;
        border: 1px solid rgba(26,20,16,0.1) !important;
        background: linear-gradient(135deg, #2d2420 0%, #1a1410 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        padding: 0.9rem 2rem !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
        box-shadow: 
            0 10px 25px rgba(26,20,16,0.15),
            0 4px 8px rgba(26,20,16,0.08),
            inset 0 1px 0 rgba(255,255,255,0.1) !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3d3530 0%, #2d2420 100%) !important;
        transform: translateY(-2px);
        box-shadow: 
            0 15px 35px rgba(26,20,16,0.25),
            0 6px 12px rgba(26,20,16,0.12),
            inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }

    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 
            0 5px 15px rgba(26,20,16,0.15),
            0 2px 4px rgba(26,20,16,0.06) !important;
    }

    /* Tabs with 3D Effect */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        padding-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, rgba(248,245,240,0.3) 100%) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        color: #7c6b5d !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(248,245,240,0.5) 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(168,85,247,0.1) 100%) !important;
        color: #1a1410 !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
        box-shadow: 
            0 8px 20px rgba(139,92,246,0.15),
            inset 0 1px 0 rgba(255,255,255,0.5) !important;
    }

    /* Metrics with 3D Depth */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(254,252,232,0.6) 0%, rgba(253,230,138,0.3) 100%);
        border: 1px solid rgba(217,119,6,0.2);
        border-radius: 18px;
        padding: 1.75rem;
        box-shadow: 
            0 12px 28px rgba(217,119,6,0.08),
            0 4px 10px rgba(217,119,6,0.04),
            inset 0 1px 0 rgba(255,255,255,0.6);
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 16px 40px rgba(217,119,6,0.12),
            0 6px 14px rgba(217,119,6,0.06),
            inset 0 1px 0 rgba(255,255,255,0.8);
    }

    /* Expander with 3D Effect */
    .stExpander {
        border: 1px solid rgba(0,0,0,0.06) !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(248,245,240,0.5) 100%) !important;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04) !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
    }

    .stExpander:hover {
        box-shadow: 0 12px 30px rgba(0,0,0,0.08) !important;
    }

    /* Text Area with Natural Styling */
    .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(248,245,240,0.6) 100%) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
    }

    .stTextArea textarea:focus {
        border-color: rgba(139,92,246,0.3) !important;
        box-shadow: 
            0 8px 20px rgba(139,92,246,0.1),
            inset 0 1px 0 rgba(255,255,255,0.6) !important;
    }

    /* File Uploader */
    .stFileUploader {
        border-radius: 14px !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.7) 0%, rgba(248,245,240,0.5) 100%);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Smooth scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.02);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(0,0,0,0.1);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# --- Load Model ---
@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color: #1a1410; font-weight: 700; font-family: Playfair Display, serif;'>SUMMARIZER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7c6b5d; font-size: 0.85rem; letter-spacing: 0.08em;'>INTELLIGENT DISTILLATION</p>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.selectbox("WORKSPACE", ["01_HOME", "02_ANALYTICS", "03_ABOUT"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("**CONFIGURATION**")
    method = st.radio("MODEL", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("DEPTH", 1, 10, 3)
    
    st.markdown("---")
    st.caption("ENGINE_REF: NATURAL_3D_V1.0")

# --- Home Page ---
if "01_HOME" in choice:
    st.markdown('<div class="header-container"><h1>Document Summarization <br> System</h1><p class="tagline">Natural Intelligence</p></div>', unsafe_allow_html=True)

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
                    st.markdown("<p style='font-weight: 700; color: #1a1410; font-size: 0.95rem;'>ORIGINAL_SOURCE</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="card-3d card-accent-green" style="font-size: 0.95rem; line-height: 1.6;">{doc["original"][:1200]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p style='font-weight: 700; color: #1a1410; font-size: 0.95rem;'>DISTILLED_CORE</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="card-3d card-accent-purple" style="font-size: 0.95rem; line-height: 1.6; font-weight: 500;">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                # Export
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                a1.download_button("EXPORT_TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_CORE.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("EXPORT_PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_CORE.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif "02_ANALYTICS" in choice:
    st.markdown('<div class="header-container"><h1>DATA<br>METRICS.</h1><p class="tagline">Quantitative Analysis</p></div>', unsafe_allow_html=True)
    
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
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'), color="#8b5cf6")

else:
    st.markdown('<div class="header-container"><h1>ABOUT<br>SYSTEM.</h1><p class="tagline">Technical Specifications</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### PHILOSOPHY
    SUMMARIZER.AI. WE BELIEVE PROFESSIONAL TOOLS SHOULD BE BOTH POWERFUL AND PLEASANT TO NAVIGATE.
    
    ### ARCHITECTURE
    - **MODEL:** NLTK + TF-IDF
    - **UI:** NATURAL 3D GLASS-MORPHISM
    - **TYPOGRAPHY:** PLAYFAIR DISPLAY + INTER
    - **PALETTE:** ORGANIC EARTH TONES WITH NATURAL GRADIENTS
    """)
    
    st.info("SYSTEM_STATUS: OPERATIONAL")
