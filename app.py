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

# --- Modern Premium CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global resets and font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0F172A;
    }

    .main {
        background-color: #FFFFFF;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] .stSelectbox label {
        font-weight: 600;
        color: #64748B;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Typography */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: #0F172A !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    .subtitle {
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        background-color: #0F172A;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
    }

    .stButton > button:hover {
        background-color: #1E293B;
        border: none;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    /* Primary Button (Start Summarizing) */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stButton > button {
        background: linear-gradient(135deg, #0F172A 0%, #334155 100%);
    }

    /* Cards / Containers */
    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 1rem !important;
    }

    div[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #0F172A !important;
    }

    /* Input Areas */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FAFAFA !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }

    .stTextArea textarea:focus {
        border-color: #0F172A !important;
        box-shadow: 0 0 0 1px #0F172A !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }

    [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    /* Alerts */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #F8FAFC !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent !important;
        border: none !important;
        color: #64748B !important;
        font-weight: 500 !important;
    }

    .stTabs [aria-selected="true"] {
        color: #0F172A !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #0F172A !important;
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
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 2rem;'>
            <div style='background: #0F172A; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center;'>
                <span style='color: white; font-weight: 800; font-size: 20px;'>S</span>
            </div>
            <span style='font-weight: 700; font-size: 1.2rem; color: #0F172A;'>Summarizer AI</span>
        </div>
    """, unsafe_allow_html=True)
    
    choice = st.selectbox("NAVIGATION", ["Home", "Analytics", "Project Info"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
            <div style='background: #F1F5F9; padding: 1.2rem; border-radius: 12px; border: 1px solid #E2E8F0;'>
                <p style='font-size: 0.85rem; color: #475569; margin: 0;'>
                    <b>Tip:</b> TF-IDF works best for technical papers with specific terminology.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- Main Content ---
if choice == "Home":
    st.markdown("<h1>AI Document Summarizer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Transform long documents into concise, actionable insights using advanced NLP.</p>", unsafe_allow_html=True)

    # Input Section
    col_input, col_settings = st.columns([2, 1], gap="large")

    with col_input:
        option = st.segmented_control(
            "Input Method",
            ["Type Text", "Single File", "Multiple Files"],
            default="Type Text"
        )
        
        documents_input = []
        error_msgs = []

        if option == "Type Text":
            text_data = st.text_area("DOCUMENT CONTENT", height=300, placeholder="Paste your text here for instant summarization...")
            if text_data and text_data.strip():
                documents_input = [("Pasted Text", text_data)]

        elif option == "Single File":
            file = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"], label_visibility="collapsed")
            if file:
                temp_path = f"temp_{file.name}"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    text_data = read_file(temp_path)
                    documents_input = [(file.name, text_data)]
                except Exception as e:
                    error_msgs.append(f"**{file.name}**: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

        else:
            files = st.file_uploader("Upload multiple files", type=["txt", "pdf"], accept_multiple_files=True, label_visibility="collapsed")
            if files:
                for file in files:
                    temp_path = f"temp_{file.name}"
                    try:
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        text_data = read_file(temp_path)
                        documents_input.append((file.name, text_data))
                    except Exception as e:
                        error_msgs.append(f"**{file.name}**: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

        for msg in error_msgs:
            st.error(f"⚠️ {msg}")

    with col_settings:
        st.markdown("<p style='font-weight: 600; color: #64748B; font-size: 0.8rem; letter-spacing: 0.05em;'>SETTINGS</p>", unsafe_allow_html=True)
        method = st.radio("Algorithm", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        num_sent = st.slider("Summary Length (Sentences)", 1, 10, 3)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Summary", type="primary"):
            if not documents_input:
                st.warning("Please provide some text first.")
            else:
                with st.spinner("Processing..."):
                    results = []
                    for name, text in documents_input:
                        try:
                            result = model.summarize(text, method, num_sent)
                            if result.strip():
                                results.append({"name": name, "original": text, "summary": result})
                        except Exception as e:
                            st.error(f"Error: {e}")
                    
                    if results:
                        st.session_state['documents'] = results
                        st.session_state['method'] = method

    # Results Section
    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("---")
        st.markdown("<h3 style='margin-bottom: 1.5rem;'>Results</h3>", unsafe_allow_html=True)
        
        docs = st.session_state['documents']
        
        for doc in docs:
            with st.expander(f"📄 {doc['name']}", expanded=True):
                tab1, tab2 = st.tabs(["Comparison", "Export"])
                
                with tab1:
                    c1, c2 = st.columns(2, gap="medium")
                    with c1:
                        st.markdown("<p style='font-weight: 600; font-size: 0.8rem; color: #64748B;'>ORIGINAL</p>", unsafe_allow_html=True)
                        st.text_area(f"orig_{doc['name']}", doc['original'], height=250, label_visibility="collapsed", disabled=True)
                    with c2:
                        st.markdown("<p style='font-weight: 600; font-size: 0.8rem; color: #64748B;'>SUMMARY</p>", unsafe_allow_html=True)
                        st.text_area(f"sum_{doc['name']}", doc['summary'], height=250, label_visibility="collapsed")
                
                with tab2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    e1, e2 = st.columns(2)
                    e1.download_button("Download as TXT", generate_txt_bytes(doc['summary']), f"{doc['name']}_summary.txt", "text/plain", key=f"t_{doc['name']}")
                    try:
                        e2.download_button("Download as PDF", generate_pdf_bytes(doc['summary']), f"{doc['name']}_summary.pdf", "application/pdf", key=f"p_{doc['name']}")
                    except:
                        pass

        if len(docs) > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container():
                st.markdown("<p style='font-weight: 600; color: #64748B; font-size: 0.8rem;'>BULK ACTIONS</p>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                sections = [(d['name'], d['summary']) for d in docs]
                b1.download_button("Download All (TXT)", generate_combined_txt_bytes(sections), "all_summaries.txt")
                try:
                    b2.download_button("Download All (PDF)", generate_pdf_bytes_multi(sections), "all_summaries.pdf")
                except:
                    pass

elif choice == "Analytics":
    st.markdown("<h1>Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Deep dive into document structure and keyword importance.</p>", unsafe_allow_html=True)
    
    docs = st.session_state.get('documents', [])
    if not docs:
        st.info("Summarize a document first to see analytics.")
    else:
        selected_doc = st.selectbox("Select Document", [d['name'] for d in docs])
        doc_data = next(d for d in docs if d['name'] == selected_doc)
        
        try:
            stats = model.get_analytics(doc_data['original'], st.session_state.get('method', 'Simple Frequency'))
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Sentences", stats['num_sentences'])
            m2.metric("Word Count", stats['num_words'])
            m3.metric("Keywords", len(stats['keywords']))
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_chart, col_table = st.columns([1, 1], gap="large")
            
            with col_chart:
                st.markdown("<p style='font-weight: 600; color: #64748B; font-size: 0.8rem;'>WORD FREQUENCY</p>", unsafe_allow_html=True)
                if stats['word_freq']:
                    df = pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count'])
                    st.bar_chart(df.set_index('Word'), color="#0F172A")
            
            with col_table:
                st.markdown("<p style='font-weight: 600; color: #64748B; font-size: 0.8rem;'>TOP SENTENCES</p>", unsafe_allow_html=True)
                st.dataframe(stats['sentence_scores'].head(10), use_container_width=True)
                
        except Exception as e:
            st.error(f"Could not load analytics: {e}")

else:
    st.markdown("<h1>Project Info</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Technical specifications and project details.</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;'>
            <div style='background: #F8FAFC; padding: 2rem; border-radius: 16px; border: 1px solid #E2E8F0;'>
                <h4 style='margin-top:0'>The System</h4>
                <p style='color: #64748B; font-size: 0.95rem;'>
                    An extractive summarization engine built with NLTK and Scikit-learn. 
                    It analyzes text structure to identify high-value sentences without 
                    altering the original meaning.
                </p>
                <ul style='color: #64748B; font-size: 0.9rem;'>
                    <li>NLTK Punkt Tokenization</li>
                    <li>TF-IDF Vectorization</li>
                    <li>PDF/TXT Parsing</li>
                </ul>
            </div>
            <div style='background: #F8FAFC; padding: 2rem; border-radius: 16px; border: 1px solid #E2E8F0;'>
                <h4 style='margin-top:0'>Metadata</h4>
                <table style='width: 100%; font-size: 0.9rem; color: #64748B;'>
                    <tr><td style='padding: 0.5rem 0;'><b>Version</b></td><td style='text-align: right;'>2.1.0</td></tr>
                    <tr><td style='padding: 0.5rem 0;'><b>Framework</b></td><td style='text-align: right;'>Streamlit</td></tr>
                    <tr><td style='padding: 0.5rem 0;'><b>License</b></td><td style='text-align: right;'>MIT</td></tr>
                    <tr><td style='padding: 0.5rem 0;'><b>Engine</b></td><td style='text-align: right;'>Teyzix Core</td></tr>
                </table>
            </div>
        </div>
    """, unsafe_allow_html=True)
