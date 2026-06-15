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
st.set_page_config(page_title="AI Document Summarizer", page_icon="📄", layout="wide")


# --- Load the summarizer (cached so it doesn't reload every run) ---
@st.cache_resource
def get_model():
    return DocumentSummarizer()


model = get_model()

# --- Sidebar ---
st.sidebar.title("Menu")
choice = st.sidebar.selectbox("Select Page", ["Home", "Analytics", "About"])

st.title("📄 AI Document Summarizer")
st.caption("Extractive summarization using NLTK & TF-IDF — Teyzix Core Internship Project")
st.markdown("---")

if choice == "Home":
    st.subheader("Summarize Your Document(s)")

    option = st.selectbox(
        "How do you want to provide text?",
        ["Type it here", "Upload a file", "Upload multiple files (multi-document)"],
    )

    # documents_input: list of (name, text)
    documents_input = []
    error_msgs = []

    if option == "Type it here":
        text_data = st.text_area("Paste your text here:", height=200)
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
        st.markdown("### Settings")
        st.caption(f"{len(documents_input)} document(s) ready to summarize.")
        col1, col2 = st.columns(2)
        with col1:
            method = st.radio("Summarization method:", ["Simple Frequency", "TF-IDF"])
        with col2:
            num_sent = st.slider("Number of sentences per summary:", 1, 10, 3)

        if st.button("Start Summarizing", type="primary"):
            with st.spinner("Summarizing..."):
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
        st.success(f"Summary generated for {len(docs)} document(s)!")

        for doc in docs:
            container = st.expander(f"📄 {doc['name']}", expanded=(len(docs) == 1))
            with container:
                st.markdown("**Original vs Summarized Text**")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original**")
                    st.text_area(
                        f"original_{doc['name']}", doc['original'], height=220,
                        label_visibility="collapsed",
                    )
                with c2:
                    st.markdown("**Summary**")
                    st.text_area(
                        f"summary_{doc['name']}", doc['summary'], height=220,
                        label_visibility="collapsed",
                    )

                d1, d2 = st.columns(2)
                d1.download_button(
                    "⬇️ Download summary (.txt)",
                    data=generate_txt_bytes(doc['summary']),
                    file_name=f"{os.path.splitext(doc['name'])[0]}_summary.txt",
                    mime="text/plain",
                    key=f"txt_{doc['name']}",
                )
                try:
                    pdf_bytes = generate_pdf_bytes(doc['summary'])
                    d2.download_button(
                        "⬇️ Download summary (.pdf)",
                        data=pdf_bytes,
                        file_name=f"{os.path.splitext(doc['name'])[0]}_summary.pdf",
                        mime="application/pdf",
                        key=f"pdf_{doc['name']}",
                    )
                except Exception as e:
                    d2.error(f"PDF export failed: {e}")

        # Combined export when multiple documents are summarized at once
        if len(docs) > 1:
            st.markdown("### Export All Summaries")
            sections = [(doc['name'], doc['summary']) for doc in docs]
            e1, e2 = st.columns(2)
            e1.download_button(
                "⬇️ Download all summaries (.txt)",
                data=generate_combined_txt_bytes(sections),
                file_name="all_summaries.txt",
                mime="text/plain",
            )
            try:
                combined_pdf = generate_pdf_bytes_multi(sections)
                e2.download_button(
                    "⬇️ Download all summaries (.pdf)",
                    data=combined_pdf,
                    file_name="all_summaries.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                e2.error(f"Combined PDF export failed: {e}")

elif choice == "Analytics":
    st.subheader("Document Analytics")

    docs = st.session_state.get('documents', [])
    if docs:
        if len(docs) > 1:
            names = [doc['name'] for doc in docs]
            selected_name = st.selectbox("Choose a document to analyze:", names)
            selected_doc = next(doc for doc in docs if doc['name'] == selected_name)
        else:
            selected_doc = docs[0]
            st.caption(f"Analyzing: **{selected_doc['name']}**")

        try:
            data = model.get_analytics(
                selected_doc['original'],
                st.session_state.get('method', 'Simple Frequency'),
            )

            a1, a2, a3 = st.columns(3)
            a1.metric("Total Sentences", data['num_sentences'])
            a2.metric("Total Words (clean)", data['num_words'])
            a3.metric("Top Keywords", ", ".join(data['keywords']) if data['keywords'] else "—")

            st.markdown("#### Word Frequency Chart")
            if data['word_freq']:
                df = pd.DataFrame(list(data['word_freq'].items()), columns=['Word', 'Count'])
                st.bar_chart(df.set_index('Word'))
            else:
                st.info("No word frequency data available.")

            st.markdown("#### Sentence Importance Scores")
            st.caption(
                "Higher scores indicate sentences the algorithm considered "
                "more important when building the summary."
            )
            if not data['sentence_scores'].empty:
                st.dataframe(data['sentence_scores'], use_container_width=True)
            else:
                st.info("No sentence scores available.")

        except Exception as e:
            st.error(f"⚠️ Could not compute analytics: {e}")
    else:
        st.warning("Please summarize a document on the Home page first!")

else:
    st.subheader("Project Info")
    st.write("**Project:** AI-Powered Document Summarization System")
    st.write("**Task ID:** AI-INT-1")
    st.write("**Domain:** Artificial Intelligence / NLP")
    st.write("**Developed by:** AI Intern")
    st.write("**Company:** TEYZIX CORE")
    st.markdown("---")
    st.markdown(
        """
**Features**

- Input: typed text, `.txt` file, single `.pdf` file, or multiple files at once
- Preprocessing: lowercasing, stopword removal, tokenization, sentence segmentation (NLTK)
- Summarization: Simple Frequency-based and TF-IDF-based extractive summarization
- Output: side-by-side original vs. summary for each document, adjustable summary length
- Multi-document support: summarize several files in one pass, with per-document and
  combined export options
- Analytics: word frequency chart, top keywords, sentence importance scores (per document)
- Export: download summaries as `.txt` or `.pdf`
"""
    )
