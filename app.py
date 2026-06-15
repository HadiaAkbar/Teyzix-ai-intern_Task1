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
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(, unsafe_allow_html=True)
@st.cache_resource
def get_model():
    return DocumentSummarizer()
model = get_model()
with st.sidebar:
    st.markdown("<h2 style='color: 
    st.markdown("<p style='color: 
    st.markdown("---")
    choice = st.selectbox("WORKSPACE", ["HOME", "ANALYTICS", "ABOUT"])
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("**CONFIGURATION**")
    method = st.radio("MODEL", ["Simple Frequency", "TF-IDF"], label_visibility="collapsed")
    num_sent = st.slider("DEPTH", 1, 10, 3)
    st.markdown("---")
    st.caption("ENGINE_REF: AI_INTERN_V1.0 🤖")
if "01_HOME" in choice:
    st.markdown('<div class="header-container"><h1>Document Summarization <br> System</h1><p class="tagline">Powered by AI Intern 🤖</p></div>', unsafe_allow_html=True)
    with st.container():
        t1, t2, t3 = st.tabs(["01_TEXT", "02_FILE", "03_BATCH"])
        documents_input = []
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            text_data = st.text_area("INPUT", height=300, placeholder="INSERT TEXT DATA HERE... I'm ready to read! 📖", label_visibility="collapsed")
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
                    st.error(f"Oops! Something went wrong: {e} 😅")
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
                        st.error(f"Oops! Something went wrong with {f.name}: {e} 😅")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("RUN_DISTILLATION", use_container_width=True):
        if not documents_input:
            st.warning("I need some text to summarize! Please provide some input. 🥺")
        else:
            with st.spinner("Processing... My neural networks are firing! 🧠✨"):
                results = []
                for name, text in documents_input:
                    try:
                        res = model.summarize(text, method, num_sent)
                        if res.strip():
                            results.append({"name": name, "original": text, "summary": res})
                    except Exception as e:
                        st.error(f"PROCESS_ERR: {e} 🚨")
                if results:
                    st.session_state['documents'] = results
                    st.session_state['method'] = method
    if 'documents' in st.session_state and st.session_state['documents']:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("
        for doc in st.session_state['documents']:
            with st.expander(f"DOCUMENT: {doc['name'].upper()}", expanded=True):
                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    st.markdown("<p style='font-weight: 700; color: 
                    st.markdown(f'<div class="card-3d card-mint" style="font-size: 0.95rem; line-height: 1.6;">{doc["original"][:1200]}...</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("<p style='font-weight: 700; color: 
                    st.markdown(f'<div class="card-3d card-lavender" style="font-size: 0.95rem; line-height: 1.6; font-weight: 500;">{doc["summary"]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                a1.download_button("EXPORT_TXT 📄", generate_txt_bytes(doc['summary']), f"{doc['name']}_CORE.txt", key=f"t_{doc['name']}")
                try:
                    a2.download_button("EXPORT_PDF 📑", generate_pdf_bytes(doc['summary']), f"{doc['name']}_CORE.pdf", key=f"p_{doc['name']}")
                except:
                    pass
elif "02_ANALYTICS" in choice:
    st.markdown('<div class="header-container"><h1>DATA<br>METRICS.</h1><p class="tagline">Crunching the numbers for you! 🤓</p></div>', unsafe_allow_html=True)
    docs = st.session_state.get('documents', [])
    if not docs:
        st.warning("I don't have any data to analyze yet! Please run a summary on the HOME page first. 🥺")
    else:
        selected = st.selectbox("SELECT_FILE", [d['name'] for d in docs])
        doc = next(d for d in docs if d['name'] == selected)
        stats = model.get_analytics(doc['original'], st.session_state.get('method', 'Simple Frequency'))
        m1, m2, m3 = st.columns(3)
        m1.metric("SENTENCES 📏", stats['num_sentences'])
        m2.metric("WORDS 🔤", stats['num_words'])
        m3.metric("TOP KEYWORD 🔑", stats['keywords'][0].upper() if stats['keywords'] else "N/A")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("
        st.bar_chart(pd.DataFrame(list(stats['word_freq'].items()), columns=['Word', 'Count']).set_index('Word'), color="
else:
    st.markdown('<div class="header-container"><h1>ABOUT<br>SYSTEM.</h1><p class="tagline">Technical Specifications 🛠️</p></div>', unsafe_allow_html=True)
    st.markdown()
    st.info("SYSTEM_STATUS: OPERATIONAL AND READY TO ASSIST! 🫡")
