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


st.set_page_config(
    page_title="SUMMARIZER.AI",
    page_icon="☁️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-color: #E0E5EC;
        --text-color: #4A4A4A;
        --text-light: #718096;
        --shadow-light: #FFFFFF;
        --shadow-dark: #A3B1C6;
        --pastel-blue: #E3F2FD;
        --pastel-purple: #F3E5F5;
    }

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: var(--text-color);
        background-color: var(--bg-color);
    }

    /* Neumorphic Container */
    .neu-container {
        background-color: var(--bg-color);
        border-radius: 50px;
        box-shadow: 20px 20px 60px var(--shadow-dark), 
                   -20px -20px 60px var(--shadow-light);
        padding: 3rem;
        margin-bottom: 3rem;
    }

    /* Neumorphic Inset */
    .neu-inset {
        background-color: var(--bg-color);
        border-radius: 30px;
        box-shadow: inset 8px 8px 16px var(--shadow-dark), 
                    inset -8px -8px 16px var(--shadow-light);
        padding: 2rem;
        margin-bottom: 1.5rem;
    }

    /* Neumorphic Button */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        padding: 1rem 2rem;
        background-color: var(--bg-color);
        color: var(--text-color);
        font-weight: 600;
        border: none;
        box-shadow: 6px 6px 12px var(--shadow-dark), 
                    -6px -6px 12px var(--shadow-light);
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        box-shadow: 2px 2px 5px var(--shadow-dark), 
                    -2px -2px 5px var(--shadow-light);
        transform: translateY(1px);
        color: #2D3748;
    }

    .stButton>button:active {
        box-shadow: inset 4px 4px 8px var(--shadow-dark), 
                    inset -4px -4px 8px var(--shadow-light);
    }

    /* Header Styling */
    .header-section {
        text-align: center;
        padding: 4rem 1rem;
    }

    .header-section h1 {
        font-weight: 800;
        font-size: 4.5rem;
        color: var(--text-color);
        letter-spacing: -2px;
        margin-bottom: 0.5rem;
    }

    .tagline {
        font-weight: 400;
        font-size: 1.1rem;
        color: var(--text-light);
        letter-spacing: 1px;
    }

    /* Sidebar Branding */
    [data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: none;
    }

    .sidebar-logo {
        font-weight: 800;
        font-size: 1.8rem;
        color: var(--text-color);
        margin-bottom: 2rem;
    }

    /* Neumorphic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--bg-color);
        border-radius: 15px;
        padding: 10px 25px;
        color: var(--text-light);
        font-weight: 500;
        box-shadow: 4px 4px 8px var(--shadow-dark), 
                    -4px -4px 8px var(--shadow-light);
        border: none;
        margin-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        box-shadow: inset 4px 4px 8px var(--shadow-dark), 
                    inset -4px -4px 8px var(--shadow-light) !important;
        color: var(--text-color) !important;
    }

    /* Result Panels */
    .neu-panel {
        border-radius: 25px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        line-height: 1.7;
    }

    .panel-blue { background-color: var(--pastel-blue); box-shadow: inset 4px 4px 8px #C1D5E3, inset -4px -4px 8px #FFFFFF; }
    .panel-purple { background-color: var(--pastel-purple); box-shadow: inset 4px 4px 8px #D6C9D9, inset -4px -4px 8px #FFFFFF; }

    /* Neumorphic Metrics */
    .metric-card {
        background-color: var(--bg-color);
        padding: 2rem;
        border-radius: 30px;
        text-align: center;
        box-shadow: 10px 10px 20px var(--shadow-dark), 
                    -10px -10px 20px var(--shadow-light);
    }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-light);
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-color);
    }

</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()


with st.sidebar:
    st.markdown('<div class="sidebar-logo">Summarizer.AI</div>', unsafe_allow_html=True)
    choice = st.selectbox("WORKSPACE", ["Home", "Analytics", "About"])
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: var(--text-light); text-transform: uppercase;'>Config</p>", unsafe_allow_html=True)
    method = st.radio("Method", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("Depth", 1, 10, 3)
    st.markdown("---")
    st.caption("AI Intern • Neumorphic Edition")


if choice == "Home":
    st.markdown('<div class="header-section"><h1>Document Summarization System </h1><p class="tagline">AI-Powered: 3D Intelligent Summarization Platform</p></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="neu-container">', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["Manual Input", "File Upload", "Batch Mode"])
        documents_input = []
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            text_data = st.text_area("INPUT", height=300, placeholder="Paste your content here...", label_visibility="collapsed")
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
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c_btn, _ = st.columns([1, 2])
    with c_btn:
        if st.button("Generate Summary"):
            if not documents_input:
                st.warning("Please provide some input.")
            else:
                with st.spinner("Analyzing..."):
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
        st.markdown("<h3 style='font-weight: 700;'>Generated Reports</h3>", unsafe_allow_html=True)
        for doc in st.session_state['documents']:
            with st.expander(f"Report: {doc['name']}", expanded=True):
                c1, c2 = st.columns(2, gap="large")
                with c1:
                    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: var(--text-light); text-transform: uppercase; margin-bottom: 1rem;'>Original Text</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="neu-panel panel-blue">{doc["original"][:1500]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: var(--text-light); text-transform: uppercase; margin-bottom: 1rem;'>AI Summary</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="neu-panel panel-purple" style="font-weight: 500;">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2, _ = st.columns([1, 1, 2])
                a1.download_button("Export TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("Export PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif choice == "Analytics":
    st.markdown('<div class="header-section"><h1>Data Metrics.</h1><p class="tagline">Linguistic distribution and analytics</p></div>', unsafe_allow_html=True)
    docs = st.session_state.get('documents', [])
    if not docs:
        st.info("Please run a summary on the Home page to see metrics.")
    else:
        selected = st.selectbox("Select Document", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><p class="metric-label">Sentences</p><p class="metric-value">{stats["num_sentences"]}</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><p class="metric-label">Words</p><p class="metric-value">{stats["num_words"]}</p></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><p class="metric-label">Top Keyword</p><p class="metric-value" style="font-size: 1.5rem; padding-top: 10px;">{stats["keywords"][0].upper() if stats["keywords"] else "N/A"}</p></div>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 700;'>Frequency Distribution</h4>", unsafe_allow_html=True)
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'))

else:
    st.markdown('<div class="header-section"><h1>System.</h1><p class="tagline">Engine Specifications</p></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="neu-container">
        <h4 style="font-weight: 700;">Architecture</h4>
        <p style="color: var(--text-light); line-height: 1.8;">
            The Summarizer.AI platform utilizes advanced statistical weighting and frequency analysis to distill large-scale content into concise, meaningful summaries. 
            The interface leverages <b>Neumorphism</b> to provide a tactile, 3D experience while maintaining a soft, modern pastel aesthetic.
        </p>
        <br>
        <p style="font-size: 0.8rem; color: var(--text-light);">Build 6.0 • Neumorphic Pastel Edition</p>
    </div>
    """, unsafe_allow_html=True)
