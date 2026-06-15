import nltk
import heapq
import io
import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2

# --- Setup NLTK data (downloads once, then cached) ---
_NLTK_RESOURCES = {
    "tokenizers/punkt": "punkt",
    "tokenizers/punkt_tab": "punkt_tab",
    "corpora/stopwords": "stopwords",
}
for path, pkg in _NLTK_RESOURCES.items():
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(pkg, quiet=True)


class DocumentSummarizer:
    """
    Extractive document summarizer using NLTK for preprocessing and
    two scoring strategies: word-frequency based and TF-IDF based.
    """

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Reserved for an optional abstractive (transformer) model.
        self.ai_model = None

    # ------------------------------------------------------------------
    # Preprocessing
    # ------------------------------------------------------------------
    def get_sentences_and_words(self, text):
        """Tokenize text into sentences and clean (lowercased, no-stopword) words."""
        if not text or not text.strip():
            return [], []
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        clean_words = [w for w in words if w.isalnum() and w not in self.stop_words]
        return sentences, clean_words

    def _word_frequencies(self, words):
        """Normalized word frequency table (0-1 range)."""
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        if freq:
            max_freq = max(freq.values())
            for w in freq:
                freq[w] = freq[w] / max_freq
        return freq

    # ------------------------------------------------------------------
    # Sentence scoring (also used by the Analytics page)
    # ------------------------------------------------------------------
    def sentence_scores_frequency(self, text):
        """Score each sentence by summing normalized word frequencies."""
        sents, words = self.get_sentences_and_words(text)
        if not sents:
            return [], {}
        freq = self._word_frequencies(words)
        scores = {}
        for s in sents:
            score = 0.0
            for w in word_tokenize(s.lower()):
                if w in freq:
                    score += freq[w]
            scores[s] = score
        return sents, scores

    def sentence_scores_tfidf(self, text):
        """Score each sentence by its summed TF-IDF weight."""
        sents, _ = self.get_sentences_and_words(text)
        if not sents:
            return [], {}
        if len(sents) == 1:
            return sents, {sents[0]: 1.0}
        vec = TfidfVectorizer(stop_words='english')
        matrix = vec.fit_transform(sents)
        raw_scores = matrix.toarray().sum(axis=1)
        scores = {s: float(raw_scores[i]) for i, s in enumerate(sents)}
        return sents, scores

    # ------------------------------------------------------------------
    # Summarization
    # ------------------------------------------------------------------
    def frequency_based_summary(self, text, count=3):
        sents, scores = self.sentence_scores_frequency(text)
        if not sents:
            return ""
        count = min(count, len(sents))
        top_sents = set(heapq.nlargest(count, scores, key=scores.get))
        # Keep original sentence order
        ordered = [s for s in sents if s in top_sents]
        return " ".join(ordered)

    def tfidf_based_summary(self, text, count=3):
        sents, scores = self.sentence_scores_tfidf(text)
        if not sents:
            return ""
        if len(sents) <= count:
            return " ".join(sents)
        top_idx = sorted(range(len(sents)), key=lambda i: scores[sents[i]], reverse=True)[:count]
        return " ".join([sents[i] for i in sorted(top_idx)])

    def summarize(self, text, method="Simple Frequency", count=3):
        """Convenience wrapper used for both single- and multi-document flows."""
        if method == "TF-IDF":
            return self.tfidf_based_summary(text, count)
        return self.frequency_based_summary(text, count)

    def abstractive_summary(self, text):
        """Placeholder for an optional transformer-based abstractive summarizer."""
        if not self.ai_model:
            return ("Abstractive (transformer-based) summarization is disabled in this "
                    "deployment for stability. Please use Simple Frequency or TF-IDF.")
        try:
            res = self.ai_model(text[:1024], max_length=130, min_length=30, do_sample=False)
            return res[0]['summary_text']
        except Exception as e:
            return f"Error generating abstractive summary: {str(e)}"

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------
    def get_analytics(self, text, method="Simple Frequency"):
        sents, words = self.get_sentences_and_words(text)
        if not words:
            return {
                "word_freq": {},
                "keywords": [],
                "num_sentences": 0,
                "num_words": 0,
                "sentence_scores": pd.DataFrame(columns=["Sentence", "Score"]),
            }

        word_counts = pd.Series(words).value_counts().head(10)

        if method == "TF-IDF":
            _, raw_scores = self.sentence_scores_tfidf(text)
        else:
            _, raw_scores = self.sentence_scores_frequency(text)

        score_df = pd.DataFrame(
            [(s, round(score, 3)) for s, score in raw_scores.items()],
            columns=["Sentence", "Score"],
        ).sort_values("Score", ascending=False).reset_index(drop=True)

        return {
            "word_freq": word_counts.to_dict(),
            "keywords": word_counts.index.tolist()[:5],
            "num_sentences": len(sents),
            "num_words": len(words),
            "sentence_scores": score_df,
        }


# ----------------------------------------------------------------------
# File handling
# ----------------------------------------------------------------------
def read_file(path):
    """Read text from a .txt or .pdf file, with error handling."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == '.pdf':
            text = ""
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if not text.strip():
                raise ValueError(
                    "No extractable text found in this PDF "
                    "(it may be a scanned/image-based document)."
                )
            return text
        else:
            raise ValueError(f"Unsupported file type: '{ext}'")
    except FileNotFoundError:
        raise RuntimeError(f"File not found: '{path}'")
    except Exception as e:
        raise RuntimeError(f"Could not read file '{path}': {e}")


# ----------------------------------------------------------------------
# Export helpers (return in-memory bytes, suitable for st.download_button)
# ----------------------------------------------------------------------
def generate_txt_bytes(text):
    """Return text encoded as bytes for a .txt download."""
    return text.encode("utf-8")


def generate_combined_txt_bytes(sections):
    """
    Build a single .txt file from multiple (title, text) sections,
    each separated by a header. Used for multi-document exports.
    """
    parts = []
    for title, text in sections:
        parts.append(f"{'=' * 10} {title} {'=' * 10}\n{text}\n")
    return "\n".join(parts).encode("utf-8")


def _draw_wrapped_text(c, text, y, width, height, margin, font_name="Helvetica", font_size=11, line_height=16):
    """Draw word-wrapped text onto a reportlab canvas, handling page breaks. Returns updated y."""
    c.setFont(font_name, font_size)

    def new_page():
        c.showPage()
        c.setFont(font_name, font_size)
        return height - 50

    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        sentences = [text] if text.strip() else []

    for sentence in sentences:
        line = sentence + "."
        words = line.split(" ")
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if c.stringWidth(candidate, font_name, font_size) < width - 2 * margin:
                current = candidate
            else:
                c.drawString(margin, y, current)
                y -= line_height
                if y < 50:
                    y = new_page()
                current = word
        if current:
            c.drawString(margin, y, current)
            y -= line_height
            if y < 50:
                y = new_page()

    return y


def generate_pdf_bytes(text):
    """Return text rendered as a simple PDF, in-memory (single document)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - 50

    _draw_wrapped_text(c, text, y, width, height, margin)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_pdf_bytes_multi(sections):
    """
    Build a single PDF from multiple (title, text) sections, each
    with its own heading. Used for multi-document exports.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - 50

    for i, (title, text) in enumerate(sections):
        if i > 0:
            # Start each new document on a fresh page for clarity
            c.showPage()
            y = height - 50

        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin, y, title)
        y -= 24

        y = _draw_wrapped_text(c, text, y, width, height, margin)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
