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
    page_title="AI Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern UI ---
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Title and Header styling */
    h1 {
        color: #1e293b;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stCaption {
        color: #64748b !important;
        font-size: 1.1rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    /* Card-like containers */
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        margin-bottom: 1rem;
    }
    
    /* Input area styling */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #4f46e5 !important;
        font-weight: 700;
    }
    
    /* Success/Info/Warning messages */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Load the summarizer (cached so it doesn't reload every run) ---
@st.cache_resource
def get_model():
    return DocumentSummarizer()

model = get_model()

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/document.png", width=80)
    st.title("Summarizer AI")
    st.markdown("---")
    choice = st.selectbox("Navigate", ["🏠 Home", "📊 Analytics", "ℹ️ About"])
    st.markdown("---")
    st.info("💡 **Pro Tip:** Use TF-IDF for better results on technical documents.")

# --- Header ---
if choice == "🏠 Home":
    st.title("📄 AI Document Summarizer")
    st.caption("Extractive summarization using NLTK & TF-IDF")
    
    st.subheader("Summarize Your Document(s)")

    option = st.selectbox(
        "How do you want to provide text?",
        ["Type it here", "Upload a file", "Upload multiple files (multi-document)"],
    )

    # documents_input: list of (name, text)
    documents_input = []
    error_msgs = []

    if option == "Type it here":
        text_data = st.text_area("Paste your text here:", height=200, placeholder="Enter your document text here...")
        if text_data and text_data.strip():
            documents_input = [("Pasted Text", text_data)]

    elif option == "Upload a file":
        file = st.file_uploader("Upload a TXT or PDF file", type=["txt", "pdf"])
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

    else:  # Upload multiple files
        files = st.file_uploader(
            "Upload multiple TXT/PDF files", type=["txt", "pdf"], accept_multiple_files=True
        )
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

    # Filter out empty documents
    documents_input = [(name, text) for name, text in documents_input if text and text.strip()]

    if documents_input:
        with st.container():
            st.markdown("### Settings")
            st.caption(f"{len(documents_input)} document(s) ready to summarize.")
            col1, col2 = st.columns(2)
            with col1:
                method = st.radio("Summarization method:", ["Simple Frequency", "TF-IDF"], horizontal=True)
            with col2:
                num_sent = st.slider("Number of sentences per summary:", 1, 10, 3)

            if st.button("Start Summarizing", type="primary", use_container_width=True):
                with st.spinner("Analyzing and summarizing..."):
                    results = []
                    for name, text in documents_input:
                        try:
                            result = model.summarize(text, method, num_sent)
                            if not result.strip():
                                st.warning(f"Couldn't generate a summary for **{name}** — the text may be too short.")
                                continue
                            results.append({"name": name, "original": text, "summary": result})
                        except Exception as e:
                            st.error(f"⚠️ Error summarizing **{name}**: {e}")

                    if results:
                        st.session_state['documents'] = results
                        st.session_state['method'] = method

    # --- Results (persist across reruns via session_state) ---
    if 'documents' in st.session_state and st.session_state['documents']:
        docs = st.session_state['documents']
        st.success(f"Successfully generated summaries for {len(docs)} document(s)!")

        for doc in docs:
            with st.expander(f"📄 {doc['name']}", expanded=(len(docs) == 1)):
                st.markdown("#### Content Comparison")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original Text**")
                    st.text_area(
                        f"original_{doc['name']}", doc['original'], height=250,
                        label_visibility="collapsed",
                    )
                with c2:
                    st.markdown("**AI Summary**")
                    st.text_area(
                        f"summary_{doc['name']}", doc['summary'], height=250,
                        label_visibility="collapsed",
                    )

                st.markdown("---")
                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(
                        "⬇️ Download Text",
                        data=generate_txt_bytes(doc['summary']),
                        file_name=f"{os.path.splitext(doc['name'])[0]}_summary.txt",
                        mime="text/plain",
                        key=f"txt_{doc['name']}",
                        use_container_width=True
                    )
                with d2:
                    try:
                        pdf_bytes = generate_pdf_bytes(doc['summary'])
                        st.download_button(
                            "⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=f"{os.path.splitext(doc['name'])[0]}_summary.pdf",
                            mime="application/pdf",
                            key=f"pdf_{doc['name']}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"PDF export failed: {e}")

        # Combined export when multiple documents are summarized at once
        if len(docs) > 1:
            st.markdown("### Export All Results")
            sections = [(doc['name'], doc['summary']) for doc in docs]
            e1, e2 = st.columns(2)
            with e1:
                st.download_button(
                    "⬇️ Download All (.txt)",
                    data=generate_combined_txt_bytes(sections),
                    file_name="all_summaries.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with e2:
                try:
                    combined_pdf = generate_pdf_bytes_multi(sections)
                    st.download_button(
                        "⬇️ Download All (.pdf)",
                        data=combined_pdf,
                        file_name="all_summaries.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Combined PDF export failed: {e}")

elif choice == "📊 Analytics":
    st.title("📊 Document Analytics")
    st.caption("Visualizing document structure and importance")

    docs = st.session_state.get('documents', [])
    if docs:
        if len(docs) > 1:
            names = [doc['name'] for doc in docs]
            selected_name = st.selectbox("Choose a document to analyze:", names)
            selected_doc = next(doc for doc in docs if doc['name'] == selected_name)
        else:
            selected_doc = docs[0]
            st.info(f"Analyzing: **{selected_doc['name']}**")

        try:
            data = model.get_analytics(
                selected_doc['original'],
                st.session_state.get('method', 'Simple Frequency'),
            )

            a1, a2, a3 = st.columns(3)
            a1.metric("Total Sentences", data['num_sentences'])
            a2.metric("Clean Words", data['num_words'])
            a3.metric("Top Keywords", ", ".join(data['keywords']) if data['keywords'] else "—")

            st.markdown("#### Word Frequency Analysis")
            if data['word_freq']:
                df = pd.DataFrame(list(data['word_freq'].items()), columns=['Word', 'Count'])
                st.bar_chart(df.set_index('Word'), color="#4f46e5")
            else:
                st.info("No word frequency data available.")

            st.markdown("#### Sentence Importance Scores")
            st.caption(
                "Scores indicate the relative importance assigned by the algorithm."
            )
            if not data['sentence_scores'].empty:
                st.dataframe(data['sentence_scores'], use_container_width=True)
            else:
                st.info("No sentence scores available.")

        except Exception as e:
            st.error(f"⚠️ Could not compute analytics: {e}")
    else:
        st.warning("Please summarize a document on the Home page first to view analytics!")

else:
    st.title("ℹ️ Project Information")
    st.caption("AI-Powered Document Summarization System")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### Overview
        This project provides an intelligent interface for extracting key information from long documents. 
        By utilizing Natural Language Processing (NLP) techniques, it identifies the most relevant 
        sentences to create concise summaries.

        ### Key Features
        - **Multi-Format Support:** Handle text files, PDFs, or direct input.
        - **Advanced Algorithms:** Choose between Frequency-based and TF-IDF methods.
        - **Bulk Processing:** Summarize multiple documents simultaneously.
        - **Data Visualization:** Explore word frequencies and importance scores.
        - **Professional Export:** Download results in TXT or PDF formats.
        """)
    
    with col2:
        st.info("""
        **Project Metadata**
        - **Domain:** AI / NLP
        - **Core:** NLTK & Scikit-learn
        - **UI:** Streamlit Modern
        - **Status:** Production Ready
        """)
    
    st.markdown("---")
    st.markdown("Developed with ❤️ by the AI Intern Team")
