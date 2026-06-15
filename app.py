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
    page_title="Summarizer AI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Violet CSS Injection ---
st.markdown("""
<style>
    /* Hide specific elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Global Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Modern Headers with Violet Gradient */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.05rem !important;
        background: linear-gradient(135deg, #C084FC 0%, #8B5CF6 50%, #6366F1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.8rem !important;
        margin-bottom: 0.5rem !important;
    }

    .subtitle {
        color: #94A3B8;
        font-size: 1.25rem;
        margin-bottom: 3.5rem;
        font-weight: 500;
    }

    /* Premium Button Styling */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: none !important;
        letter-spacing: -0.01em !important;
        padding: 0.8rem 2rem !important;
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5) !important;
    }

    /* Metric Boxes with Violet Border */
    [data-testid="stMetric"] {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        padding: 1.5rem;
        border-radius: 20px;
        transition: border-color 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: #8B5CF6;
    }

    /* Expander Styling */
    .stExpander {
        border: 1px solid #1E293B !important;
        border-radius: 16px !important;
        background-color: #0F172A !important;
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #1E293B;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #020617;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #8B5CF6;
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
    st.markdown("<h2 style='color: #C084FC;'>🔮 Summarizer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>Intelligence for the modern age.</p>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.selectbox("WORKSPACE", ["Home", "Analytics", "About"])
    
    st.markdown("---")
    st.markdown("#### Configuration")
    method = st.radio("Model Type", ["Simple Frequency", "TF-IDF"])
    num_sent = st.slider("Summary Depth", 1, 10, 3)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Engine: Teyzix Core v2.4")

# --- Home Page ---
if choice == "Home":
    st.markdown("<h1>Summarizer AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Unlock the essence of any document in seconds.</p>", unsafe_allow_html=True)

    # Main Input Area
    with st.container():
        tab_text, tab_file, tab_multi = st.tabs(["📝 Input Text", "📄 Upload File", "📚 Batch Process"])
        
        documents_input = []
        
        with tab_text:
            text_data = st.text_area("Source Content", height=350, placeholder="Paste your text here...", label_visibility="collapsed")
            if text_data.strip():
                documents_input = [("Pasted Text", text_data)]
                
        with tab_file:
            file = st.file_uploader("Choose a document", type=["txt", "pdf"], label_visibility="collapsed")
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
                        
        with tab_multi:
            files = st.file_uploader("Select multiple documents", type=["txt", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
            if files:
                for f in files:
                    temp_path = f"temp_{f.name}"
                    try:
                        with open(temp_path, "wb") as f:
                            f.write(f.getbuffer())
                        text_data = read_file(temp_path)
                        documents_input.append((f.name, text_data))
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate Summary", use_container_width=True):
        if not documents_input:
            st.warning("Please provide input content first.")
        else:
            with st.spinner("Distilling key insights..."):
                results = []
                for name, text in documents_input:
                    try:
                        res = model.summarize(text, method, num_sent)
                        if res.strip():
                            results.append({"name": name, "original": text, "summary": res})
                    except Exception as e:
                        st.error(f"Summarization Error: {e}")
                
                if results:
                    st.session_state['documents'] = results
                    st.session_state['method'] = method

    # Results Section
    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 📄 Distilled Results")
        
        for doc in st.session_state['documents']:
            with st.expander(f"Analysis: {doc['name']}", expanded=True):
                col_left, col_right = st.columns(2, gap="large")
                with col_left:
                    st.markdown("<p style='color: #64748B; font-weight: 600; font-size: 0.8rem;'>ORIGINAL</p>", unsafe_allow_html=True)
                    st.info(doc['original'][:1000] + ("..." if len(doc['original']) > 1000 else ""))
                with col_right:
                    st.markdown("<p style='color: #8B5CF6; font-weight: 600; font-size: 0.8rem;'>AI SUMMARY</p>", unsafe_allow_html=True)
                    st.success(doc['summary'])
                
                # Export Options
                st.markdown("<br>", unsafe_allow_html=True)
                e1, e2 = st.columns(2)
                e1.download_button("Download Text", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", key=f"t_{doc['name']}")
                try:
                    e2.download_button("Download PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif choice == "Analytics":
    st.markdown("<h1>Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Quantifying the importance of your data.</p>", unsafe_allow_html=True)
    
    docs = st.session_state.get('documents', [])
    if not docs:
        st.warning("Summarize a document to unlock analytics.")
    else:
        selected = st.selectbox("SELECT DOCUMENT", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Sentences", stats['num_sentences'])
        m2.metric("Word Count", stats['num_words'])
        m3.metric("Key Keyword", stats['keywords'][0] if stats['keywords'] else "None")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'), color="#8B5CF6")

else:
    st.markdown("<h1>Project Info</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>The technology behind the intelligence.</p>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("""
        ### The Philosophy
        We believe that in an age of information overload, the ability to distill 
        complex documents into clear, actionable summaries is a superpower. 
        Summarizer AI is built to provide that clarity.
        """)
    with col_b:
        st.markdown("""
        ### Technical Stack
        - **Model:** NLTK + TF-IDF Vectorization
        - **UI:** Streamlit Premium Design
        - **Typography:** Plus Jakarta Sans
        - **Color:** Violet/Indigo Deep Slate
        """)
    
    st.info("Built for efficiency • Powered by Teyzix Core")
