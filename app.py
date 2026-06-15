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
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern 3D/Glassmorphism CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background Gradient */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* 3D Header Container */
    .header-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 
                    inset 0 1px 1px rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin-bottom: 3rem;
        transform: perspective(1000px) rotateX(2deg);
        transition: transform 0.3s ease;
    }
    
    .header-container:hover {
        transform: perspective(1000px) rotateX(0deg) translateY(-5px);
    }

    .header-container h1 {
        font-weight: 800;
        background: linear-gradient(90deg, #4A90E2, #9C27B0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        letter-spacing: -1px;
    }

    .tagline {
        color: #555;
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }

    /* 3D Cards */
    .card-3d {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05), 
                    0 6px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        margin-bottom: 1.5rem;
    }

    .card-3d:hover {
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }

    .card-mint { border-left: 8px solid #00d2ff; }
    .card-lavender { border-left: 8px solid #9C27B0; }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
        background: linear-gradient(135deg, #357ABD 0%, #4A90E2 100%);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255,255,255,0.5);
        padding: 10px;
        border-radius: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 10px;
        color: #4A90E2;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .stTabs [aria-selected="true"] {
        background: #4A90E2 !important;
        color: white !important;
    }

    /* Sidebar Logo/Title */
    .sidebar-title {
        font-weight: 800;
        font-size: 1.5rem;
        color: #1A1A1A;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()

with st.sidebar:
    st.markdown('<div class="sidebar-title">SUMMARIZER.AI ✨</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #666; font-size: 0.9rem;'>Next-gen document intelligence</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    choice = st.selectbox("WORKSPACE", ["HOME", "ANALYTICS", "ABOUT"])
    st.markdown("---")
    st.markdown("**CONFIGURATION**")
    method = st.radio("MODEL", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("DEPTH", 1, 10, 3)
    st.markdown("---")
    st.caption("ENGINE_REF: AI_INTERN_V2.0 🧠")

if choice == "HOME":
    st.markdown('<div class="header-container"><h1>Summarizer AI</h1><p class="tagline">Distilling knowledge with 3D precision ✨</p></div>', unsafe_allow_html=True)
    
    with st.container():
        t1, t2, t3 = st.tabs(["📝 TEXT INPUT", "📁 FILE UPLOAD", "📚 BATCH PROCESS"])
        documents_input = []
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            text_data = st.text_area("INPUT", height=300, placeholder="Drop your text here and let the magic happen...", label_visibility="collapsed")
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
                        st.error(f"Error with {f.name}: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ RUN DISTILLATION"):
        if not documents_input:
            st.warning("Please provide some input first!")
        else:
            with st.spinner("Analyzing content..."):
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
        st.markdown("### 📊 GENERATED INSIGHTS")
        for doc in st.session_state['documents']:
            with st.expander(f"📄 {doc['name'].upper()}", expanded=True):
                c1, c2 = st.columns(2, gap="large")
                with c1:
                    st.markdown("<p style='font-weight: 700; color: #4A90E2; margin-bottom: 10px;'>SOURCE CONTENT</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="card-3d card-mint">{doc["original"][:1500]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p style='font-weight: 700; color: #9C27B0; margin-bottom: 10px;'>AI CORE SUMMARY</p>", unsafe_allow_html=True)
                    st.markdown(f'<div class="card-3d card-lavender" style="font-weight: 500;">{doc["summary"]}</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2, _ = st.columns([1, 1, 2])
                a1.download_button("Download TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("Download PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif choice == "ANALYTICS":
    st.markdown('<div class="header-container"><h1>Data Metrics</h1><p class="tagline">Deep-dive into document statistics 📊</p></div>', unsafe_allow_html=True)
    docs = st.session_state.get('documents', [])
    if not docs:
        st.info("No data to analyze. Run a summary on the HOME page first!")
    else:
        selected = st.selectbox("Select Document", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="card-3d" style="text-align: center;"><p style="color: #666;">Sentences</p><h2>{stats["num_sentences"]}</h2></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="card-3d" style="text-align: center;"><p style="color: #666;">Words</p><h2>{stats["num_words"]}</h2></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="card-3d" style="text-align: center;"><p style="color: #666;">Top Keyword</p><h2>{stats["keywords"][0].upper() if stats["keywords"] else "N/A"}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📈 Word Frequency Analysis")
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'))

else:
    st.markdown('<div class="header-container"><h1>About System</h1><p class="tagline">The technology behind the intelligence 🛠️</p></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-3d">
        <h3>Technical Stack</h3>
        <p><b>Core:</b> Python 3.11 + Streamlit</p>
        <p><b>NLP:</b> NLTK, Scikit-Learn (TF-IDF)</p>
        <p><b>UI:</b> Custom CSS3 with Glassmorphism & 3D Effects</p>
        <p><b>Status:</b> <span style="color: #00c853;">● Operational</span></p>
    </div>
    """, unsafe_allow_html=True)
