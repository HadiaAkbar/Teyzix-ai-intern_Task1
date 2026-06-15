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
    page_icon="🌸", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Soft Pastel & Elegant Typography CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-color: #FDFBFB;
        --sidebar-bg: #FFFFFF;
        --accent-pastel: #E2E2E2;
        --pastel-blue: #E3F2FD;
        --pastel-purple: #F3E5F5;
        --pastel-pink: #FCE4EC;
        --pastel-green: #E8F5E9;
        --text-main: #2D3436;
        --text-secondary: #636E72;
    }

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: var(--text-main);
        background-color: var(--bg-color);
    }

    /* Soft 3D Shadow Style */
    .soft-shadow {
        box-shadow: 0 10px 30px rgba(0,0,0,0.03), 0 1px 8px rgba(0,0,0,0.02);
    }

    /* Elegant Header */
    .header-section {
        padding: 4rem 2rem;
        text-align: center;
        background: linear-gradient(to bottom, #FFFFFF, #FDFBFB);
        border-radius: 0 0 50px 50px;
        margin-bottom: 3rem;
    }

    .header-section h1 {
        font-family: 'DM+Serif+Display', serif;
        font-size: 4.5rem;
        color: #2D3436;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .header-tagline {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid #F1F1F1;
    }

    .sidebar-logo {
        font-family: 'DM+Serif+Display', serif;
        font-size: 1.8rem;
        color: #2D3436;
        margin-bottom: 2rem;
    }

    /* Pastel Cards */
    .pastel-card {
        background: #FFFFFF;
        padding: 2.5rem;
        border-radius: 30px;
        border: 1px solid #F8F9FA;
        box-shadow: 0 20px 40px rgba(0,0,0,0.02);
        margin-bottom: 2rem;
        transition: transform 0.4s ease;
    }

    .pastel-card:hover {
        transform: translateY(-5px);
    }

    .card-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
        color: var(--text-secondary);
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        padding: 0.8rem 2rem;
        background-color: #2D3436;
        color: #FFFFFF;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    .stButton>button:hover {
        background-color: #000000;
        transform: scale(1.02);
        color: #FFFFFF;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 12px 24px;
        background-color: #F8F9FA;
        border-radius: 15px;
        color: var(--text-secondary);
        border: 1px solid #F1F1F1;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2D3436 !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.05);
        border: 1px solid #EEE !important;
    }

    /* Custom Metric Cards */
    .metric-box {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 25px;
        text-align: center;
        border: 1px solid #F8F9FA;
        box-shadow: 0 10px 25px rgba(0,0,0,0.02);
    }
    
    .metric-value {
        font-family: 'DM+Serif+Display', serif;
        font-size: 2.5rem;
        color: #2D3436;
    }

    .metric-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Result Cards */
    .result-source { background-color: #F1F8FF; border-radius: 20px; padding: 20px; border: 1px solid #E1F0FF; }
    .result-summary { background-color: #F9F5FF; border-radius: 20px; padding: 20px; border: 1px solid #F0E5FF; }

</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Summarizer.</div>', unsafe_allow_html=True)
    choice = st.selectbox("WORKSPACE", ["Home", "Analytics", "About"])
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p class='card-title'>Configuration</p>", unsafe_allow_html=True)
    method = st.radio("Method", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("Depth", 1, 10, 3)
    st.markdown("---")
    st.caption("AI Intern v3.0 • Minimalist Edition")

# Main Content
if choice == "Home":
    st.markdown('<div class="header-section"><h1>Knowledge Distilled.</h1><p class="header-tagline">Elegant AI-powered summarization</p></div>', unsafe_allow_html=True)
    
    with st.container():
        t1, t2, t3 = st.tabs(["Text Input", "File Upload", "Batch Mode"])
        documents_input = []
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            text_data = st.text_area("INPUT", height=300, placeholder="Paste your content here...", label_visibility="collapsed")
            if text_data.strip():
                documents_input = [("Pasted Content", text_data)]
        
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
                    st.error(f"Error: {e}")
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
                        st.error(f"Error: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Summarize Content"):
        if not documents_input:
            st.warning("Please provide some input first.")
        else:
            with st.spinner("Processing..."):
                results = []
                for name, text in documents_input:
                    try:
                        res = model.summarize(text, method, num_sent)
                        if res.strip():
                            results.append({"name": name, "original": text, "summary": res})
                    except Exception as e:
                        st.error(f"Error: {e}")
                if results:
                    st.session_state['documents'] = results
                    st.session_state['method'] = method

    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p class='card-title'>Results</p>", unsafe_allow_html=True)
        for doc in st.session_state['documents']:
            with st.expander(f"Analysis: {doc['name']}", expanded=True):
                c1, c2 = st.columns(2, gap="large")
                with c1:
                    st.markdown("<p class='card-title' style='color: #3498db;'>Source</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="result-source">{doc["original"][:1500]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p class='card-title' style='color: #9b59b6;'>AI Summary</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="result-summary" style="font-weight: 500; line-height: 1.6;">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2, _ = st.columns([1, 1, 2])
                a1.download_button("Export TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("Export PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif choice == "Analytics":
    st.markdown('<div class="header-section"><h1>Metrics.</h1><p class="header-tagline">Deep linguistic analysis</p></div>', unsafe_allow_html=True)
    docs = st.session_state.get('documents', [])
    if not docs:
        st.info("Run a summary first to view analytics.")
    else:
        selected = st.selectbox("Select Document", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Sentences</p><p class="metric-value">{stats["num_sentences"]}</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Words</p><p class="metric-value">{stats["num_words"]}</p></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><p class="metric-label">Top Keyword</p><p class="metric-value" style="font-size: 1.5rem; padding-top: 10px;">{stats["keywords"][0].upper() if stats["keywords"] else "N/A"}</p></div>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p class='card-title'>Word Distribution</p>", unsafe_allow_html=True)
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'))

else:
    st.markdown('<div class="header-section"><h1>System.</h1><p class="header-tagline">Technical foundation</p></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pastel-card">
        <p class="card-title">Technical Specifications</p>
        <p>This system utilizes <b>NLTK</b> and <b>Scikit-Learn</b> to perform extractive summarization. 
        The interface is built with a focus on <b>minimalism</b> and <b>clarity</b>, using a soft pastel palette to reduce cognitive load.</p>
        <br>
        <p><b>Version:</b> 3.0.0 (Minimalist Redesign)</p>
        <p><b>Status:</b> Active</p>
    </div>
    """, unsafe_allow_html=True)
