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

# Page configuration
st.set_page_config(
    page_title="SUMMARIZER.AI",
    page_icon="🧬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Fidelity Realistic UI CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-main: #F8F9FB;
        --charcoal: #333333;
        --slate: #4A5568;
        --soft-blue: #EBF8FF;
        --glass-white: rgba(255, 255, 255, 0.9);
        --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--charcoal);
        background-color: var(--bg-main);
    }

    /* Multi-layered Realistic Shadow */
    .realistic-depth {
        box-shadow: 
            0 1px 3px rgba(0,0,0,0.02),
            0 10px 15px -3px rgba(0,0,0,0.03),
            0 4px 6px -2px rgba(0,0,0,0.01);
    }

    /* Realistic Glass Container */
    .glass-card {
        background: var(--glass-white);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.05), 
            0 2px 4px -1px rgba(0, 0, 0, 0.03),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
    }

    /* Hero Section with Light Reflection */
    .hero-section {
        padding: 5rem 2rem;
        text-align: center;
        background: radial-gradient(circle at top right, #FFFFFF, #F8F9FB);
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 3rem;
    }

    .hero-section h1 {
        font-weight: 800;
        font-size: 4rem;
        color: var(--charcoal);
        letter-spacing: -2px;
        line-height: 1;
        margin-bottom: 1rem;
    }

    .hero-tagline {
        color: var(--slate);
        font-size: 1.25rem;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #EDF2F7;
    }

    .sidebar-brand {
        font-weight: 800;
        font-size: 1.5rem;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }

    /* Realistic Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 14px;
        padding: 0.75rem 1.5rem;
        background: var(--charcoal);
        color: #FFFFFF;
        font-weight: 600;
        border: 1px solid var(--charcoal);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .stButton>button:hover {
        background: #000000;
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        color: #FFFFFF;
    }

    /* Realistic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: #EDF2F7;
        padding: 6px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: var(--slate);
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: var(--charcoal) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Result Panels */
    .panel-source {
        background: #F7FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 24px;
        color: var(--slate);
        line-height: 1.7;
    }

    .panel-summary {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        color: var(--charcoal);
        font-weight: 500;
        line-height: 1.7;
    }

    /* Realistic Metrics */
    .metric-card {
        background: #FFFFFF;
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        text-align: left;
    }

    .metric-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--slate);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .metric-val {
        font-size: 2rem;
        font-weight: 800;
        color: var(--charcoal);
    }

</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-brand">SUMMARIZER.AI</div>', unsafe_allow_html=True)
    choice = st.selectbox("WORKSPACE", ["Home", "Analytics", "About"])
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #A0AEC0; text-transform: uppercase;'>Engine Settings</p>", unsafe_allow_html=True)
    method = st.radio("Method", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("Depth", 1, 10, 3)
    st.markdown("---")
    st.caption("AI Intern v4.0 • Realistic Fidelity")

# Main Interface
if choice == "Home":
    st.markdown('<div class="hero-section"><h1>Distill Complexity.</h1><p class="hero-tagline">A high-fidelity intelligence tool designed to transform long-form content into actionable insights.</p></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["Manual Input", "File Upload", "Batch Processing"])
        documents_input = []
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            text_data = st.text_area("INPUT", height=300, placeholder="Enter or paste your text here...", label_visibility="collapsed")
            if text_data.strip():
                documents_input = [("Manual Entry", text_data)]
        
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
                    st.error(f"Processing Error: {e}")
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
                        with open(temp_path, "wb") as f_out:
                            f_out.write(f.getbuffer())
                        text_data = read_file(temp_path)
                        documents_input.append((f.name, text_data))
                    except Exception as e:
                        st.error(f"Batch Error: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c_btn, _ = st.columns([1, 2])
    with c_btn:
        if st.button("Generate Summary"):
            if not documents_input:
                st.warning("Please provide input content.")
            else:
                with st.spinner("Analyzing..."):
                    results = []
                    for name, text in documents_input:
                        try:
                            res = model.summarize(text, method, num_sent)
                            if res.strip():
                                results.append({"name": name, "original": text, "summary": res})
                        except Exception as e:
                            st.error(f"Analysis Error: {e}")
                    if results:
                        st.session_state['documents'] = results
                        st.session_state['method'] = method

    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-weight: 800; letter-spacing: -1px;'>Analysis Output</h3>", unsafe_allow_html=True)
        for doc in st.session_state['documents']:
            with st.expander(f"Report: {doc['name']}", expanded=True):
                c1, c2 = st.columns(2, gap="large")
                with c1:
                    st.markdown("<p style='font-size: 0.75rem; font-weight: 800; color: #718096; text-transform: uppercase; margin-bottom: 12px;'>Source Content</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="panel-source">{doc["original"][:1500]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p style='font-size: 0.75rem; font-weight: 800; color: #4A5568; text-transform: uppercase; margin-bottom: 12px;'>AI Core Summary</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="panel-summary">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2, _ = st.columns([1, 1, 2])
                a1.download_button("Export TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("Export PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif choice == "Analytics":
    st.markdown('<div class="hero-section"><h1>Data Intelligence.</h1><p class="hero-tagline">Quantifying linguistic patterns and keyword distributions.</p></div>', unsafe_allow_html=True)
    docs = st.session_state.get('documents', [])
    if not docs:
        st.info("No active analysis. Please run a summary on the Home page.")
    else:
        selected = st.selectbox("Select Document", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Sentences</p><p class="metric-val">{stats["num_sentences"]}</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Word Count</p><p class="metric-val">{stats["num_words"]}</p></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><p class="metric-title">Primary Keyword</p><p class="metric-val" style="font-size: 1.25rem; padding-top: 10px;">{stats["keywords"][0].upper() if stats["keywords"] else "N/A"}</p></div>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 700;'>Frequency Distribution</h4>", unsafe_allow_html=True)
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'))

else:
    st.markdown('<div class="hero-section"><h1>Technical Specs.</h1><p class="hero-tagline">Architectural overview of the summarization engine.</p></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        <h4 style="font-weight: 700; margin-bottom: 1rem;">Engine Architecture</h4>
        <p style="color: var(--slate); line-height: 1.6;">
            The system employs a dual-model extractive approach. <b>Frequency Analysis</b> prioritizes sentences containing globally significant terms, 
            while the <b>TF-IDF Vectorizer</b> uses statistical weighting to identify unique semantic markers across the document structure.
        </p>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 2rem 0;">
        <p style="font-size: 0.875rem; color: #A0AEC0;">
            Build 4.0.2 • High Fidelity Realistic UI • Stable Release
        </p>
    </div>
    """, unsafe_allow_html=True)
