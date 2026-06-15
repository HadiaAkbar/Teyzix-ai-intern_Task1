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
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Stable CSS Injection ---
# We use a single markdown block with unsafe_allow_html=True
# Note: Streamlit Cloud sometimes struggles with complex HTML in markdown, 
# so we keep it clean and use standard Streamlit components where possible.
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Modern Title */
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #1E293B !important;
        letter-spacing: -0.05rem !important;
        margin-bottom: 0rem !important;
        padding-bottom: 0rem !important;
    }

    .main-subtitle {
        font-size: 1.2rem !important;
        color: #64748B !important;
        margin-top: 0rem !important;
        margin-bottom: 2rem !important;
    }

    /* Sidebar Branding */
    .sidebar-brand {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        margin-bottom: 2rem !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Card-like containers for results */
    .result-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Custom button styling */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s !important;
    }

    /* Hide Streamlit branding */
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
    st.markdown('<div class="sidebar-brand">✨ Summarizer AI</div>', unsafe_allow_html=True)
    
    # Navigation using standard selectbox for stability
    choice = st.selectbox("GO TO", ["Home", "Analytics", "About"], index=0)
    
    st.markdown("---")
    st.markdown("**Quick Settings**")
    method = st.radio("Algorithm", ["Simple Frequency", "TF-IDF"], horizontal=False)
    num_sent = st.slider("Summary Length", 1, 10, 3)
    
    st.markdown("---")
    st.caption("v2.2.0 • Powered by Teyzix Core")

# --- Main Content ---
if choice == "Home":
    st.markdown('<h1 class="main-title">Summarize Anything.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Professional-grade document summarization powered by NLP.</p>', unsafe_allow_html=True)

    # Use a container for the input area
    with st.container():
        # Input Method Tabs
        tab_text, tab_file, tab_multi = st.tabs(["📝 Paste Text", "📄 Single File", "📚 Multiple Files"])
        
        documents_input = []
        
        with tab_text:
            text_data = st.text_area("Paste content here", height=250, placeholder="Start typing or paste your document content...", label_visibility="collapsed")
            if text_data and text_data.strip():
                documents_input = [("Pasted Text", text_data)]
                
        with tab_file:
            file = st.file_uploader("Upload a TXT or PDF file", type=["txt", "pdf"])
            if file:
                temp_path = f"temp_{file.name}"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    text_data = read_file(temp_path)
                    documents_input = [(file.name, text_data)]
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
        with tab_multi:
            files = st.file_uploader("Upload multiple files", type=["txt", "pdf"], accept_multiple_files=True)
            if files:
                for file in files:
                    temp_path = f"temp_{file.name}"
                    try:
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        text_data = read_file(temp_path)
                        documents_input.append((file.name, text_data))
                    except Exception as e:
                        st.error(f"Error reading {file.name}: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    # Summarize Button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate Summary", type="primary", use_container_width=True):
        if not documents_input:
            st.warning("Please provide some text or upload a file first.")
        else:
            with st.spinner("Analyzing document structure..."):
                results = []
                for name, text in documents_input:
                    try:
                        result = model.summarize(text, method, num_sent)
                        if result.strip():
                            results.append({"name": name, "original": text, "summary": result})
                    except Exception as e:
                        st.error(f"Summarization error: {e}")
                
                if results:
                    st.session_state['documents'] = results
                    st.session_state['method'] = method

    # Results Display
    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("---")
        st.subheader("Results")
        
        for doc in st.session_state['documents']:
            with st.expander(f"📄 {doc['name']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original Content**")
                    st.info(doc['original'][:1000] + ("..." if len(doc['original']) > 1000 else ""))
                with col2:
                    st.markdown("**AI Summary**")
                    st.success(doc['summary'])
                
                # Actions
                c1, c2 = st.columns(2)
                c1.download_button("⬇️ Download TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", "text/plain", key=f"t_{doc['name']}")
                try:
                    c2.download_button("⬇️ Download PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", "application/pdf", key=f"p_{doc['name']}")
                except:
                    pass

elif choice == "Analytics":
    st.markdown('<h1 class="main-title">Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Visualizing document metrics and importance.</p>', unsafe_allow_html=True)
    
    docs = st.session_state.get('documents', [])
    if not docs:
        st.warning("No data to analyze. Please summarize a document first.")
    else:
        selected_name = st.selectbox("Select a document to analyze", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected_name)
        
        try:
            stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Sentences", stats['num_sentences'])
            m2.metric("Word Count", stats['num_words'])
            m3.metric("Top Keywords", stats['keywords'][0] if stats['keywords'] else "N/A")
            
            st.markdown("### Word Frequency")
            if stats['word_freq']:
                df = pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count'])
                st.bar_chart(df.set_index('Word'))
            
            st.markdown("### Sentence Importance")
            st.dataframe(stats['sentence_scores'].head(10), use_container_width=True)
            
        except Exception as e:
            st.error(f"Analytics error: {e}")

else:
    st.markdown('<h1 class="main-title">About</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Technical details and project information.</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### The Engine
    Summarizer AI uses extractive summarization techniques to identify the most important sentences in a document. 
    It supports two main algorithms:
    
    1. **Simple Frequency:** Ranks sentences based on the frequency of important words.
    2. **TF-IDF:** Uses Term Frequency-Inverse Document Frequency to find sentences with unique, high-value information.
    
    ### Tech Stack
    - **Frontend:** Streamlit
    - **NLP:** NLTK, Scikit-learn
    - **Parsing:** PyPDF2
    - **Styling:** Custom CSS & Inter Typeface
    """)
    
    st.info("Developed by AI Intern • Teyzix Core")
