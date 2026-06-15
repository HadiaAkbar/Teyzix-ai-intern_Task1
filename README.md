# AI-Powered Document Summarization System

**Task ID:** AI-INT-1
**Domain:** Artificial Intelligence / NLP
**Company:** TEYZIX CORE
**Developed by:** AI Intern

## Overview

A Streamlit web app that automatically summarizes long text documents into short,
meaningful summaries while preserving key information. The app supports extractive
summarization using two scoring strategies and provides analytics on the input text.

## Link
https://teyzix-ai-interntask1-xamufj2essjf9sulyzkgja.streamlit.app/

## Features

### 1. Data Input
- Type/paste text directly
- Upload a `.txt` file
- Upload a `.pdf` file (text-based PDFs)
- Upload **multiple** `.txt`/`.pdf` files at once for multi-document summarization

### 2. Text Preprocessing (NLTK)
- Lowercasing
- Stopword removal
- Word tokenization
- Sentence segmentation

### 3. Summarization Logic
- **Simple Frequency**: scores sentences by the normalized frequency of the
  (non-stopword) words they contain.
- **TF-IDF**: scores sentences using TF-IDF weights, highlighting sentences with
  unique, distinctive terms.
- Adjustable summary length (1–10 sentences).

### 4. Output
- Side-by-side display of the original text and the generated summary for each
  document.
- Export each summary as `.txt` or `.pdf` (generated in-memory, downloaded
  directly via the browser).
- When multiple documents are summarized at once, a combined `.txt`/`.pdf`
  containing all summaries (with document titles) can also be downloaded.

### 5. Analytics
- Choose which document to analyze (when multiple were uploaded)
- Word frequency chart (top 10 words after stopword removal)
- Top 5 keywords
- Sentence importance scores table (ranked highest to lowest)

### 6. Error Handling
- Invalid/unsupported file types are rejected with a clear message.
- Scanned/image-only PDFs (no extractable text) raise a helpful error.
- Empty input or input too short to summarize is handled gracefully.

## Project Structure

```
.
├── app.py                # Streamlit UI
├── summarizer.py          # Core NLP logic (preprocessing, scoring, summarization, I/O)
├── sample_document.txt    # Sample input document for testing
├── requirements.txt       # Python dependencies
├── runtime.txt             # Pinned Python version for deployment
└── README.md
```

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

1. Choose **Home** from the sidebar, then provide text — type it, upload a single
   file, or upload multiple files for multi-document summarization.
2. Pick a summarization method (Simple Frequency or TF-IDF) and the desired
   number of summary sentences per document.
3. Click **Start Summarizing** to view each document's original text alongside
   its summary, and download results as `.txt` or `.pdf` (individually, or
   combined when multiple documents were processed).
4. Visit **Analytics** to view word frequency, top keywords, and per-sentence
   importance scores. If multiple documents were summarized, pick which one to
   analyze from the dropdown.

## Notes on the Bonus Section

- **Abstractive summarization (Transformers)**: not enabled in this deployment to
  keep the app lightweight and stable on Streamlit Cloud. The summarizer includes
  a placeholder hook (`abstractive_summary`) where a transformer pipeline could be
  added.
- **Streamlit UI**: implemented (this app).
- **Multi-document summarization**: implemented — upload multiple `.txt`/`.pdf`
  files at once, get an individual summary and analytics for each, plus a
  combined export.
- **Language detection**: not implemented in this version; noted as a possible
  future enhancement.
