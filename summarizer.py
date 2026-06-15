import nltk
import heapq
import io
import os
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
from typing import List, Dict, Set, Tuple, Any

# 🤖 AI INTERN LOG: Initializing NLTK resources! This ensures all necessary linguistic data is available. 📚
_NLTK_RESOURCES: Dict[str, str] = {
    "tokenizers/punkt": "punkt",
    "tokenizers/punkt_tab": "punkt_tab",
    "corpora/stopwords": "stopwords",
}
for path, pkg in _NLTK_RESOURCES.items():
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(pkg, quiet=True) # Downloading quietly to avoid spamming the console. Shhh! 🤫


class DocumentSummarizer:
    """
    🤖 AI INTERN DOC: This class is my core! It performs extractive document summarization.
    I use NLTK for robust text preprocessing and offer two powerful scoring strategies:
    1. Word-frequency based (simple yet effective!)
    2. TF-IDF based (great for identifying unique and important terms!)
    """

    def __init__(self) -> None:
        # 🤖 AI INTERN LOG: Loading up the English stop words. These are common words (like 'the', 'is')
        # that don't usually add much meaning to a summary, so we filter them out. 🧹
        self.stop_words: Set[str] = set(stopwords.words("english"))
        # 🤖 AI INTERN LOG: This is a placeholder for a future, more advanced abstractive model.
        # Currently, it's disabled for stability, but I dream of enabling it soon! 🚀
        self.ai_model: Any = None

    # ------------------------------------------------------------------
    # 🧠 AI INTERN MODULE: Preprocessing Functions
    # ------------------------------------------------------------------
    def get_sentences_and_words(self, text: str) -> Tuple[List[str], List[str]]:
        """🤖 AI INTERN DOC: Tokenizes input text into sentences and then cleans the words.
        Cleaning involves lowercasing, removing non-alphanumeric characters, and filtering out stop words.
        This prepares the text for accurate summarization. ✨
        """
        if not text or not text.strip():
            # 🤖 AI INTERN LOG: Handling empty input gracefully. No text, no summary! 🤷‍♀️
            return [], []
        sentences: List[str] = sent_tokenize(text)
        words: List[str] = word_tokenize(text.lower())
        clean_words: List[str] = [w for w in words if w.isalnum() and w not in self.stop_words]
        return sentences, clean_words

    def _word_frequencies(self, words: List[str]) -> Dict[str, float]:
        """🤖 AI INTERN DOC: Calculates the normalized frequency of each word.
        Normalization scales frequencies between 0 and 1, which helps in fair comparison.
        """
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        if freq:
            max_freq: int = max(freq.values())
            for w in freq:
                freq[w] = freq[w] / max_freq # Normalizing by the maximum frequency. 📊
        return freq

    # ------------------------------------------------------------------
    # 🧠 AI INTERN MODULE: Sentence Scoring Strategies
    # ------------------------------------------------------------------
    def sentence_scores_frequency(self, text: str) -> Tuple[List[str], Dict[str, float]]:
        """🤖 AI INTERN DOC: Scores each sentence based on the sum of its normalized word frequencies.
        Sentences containing more frequent (and non-stop) words get higher scores.
        """
        sents, words = self.get_sentences_and_words(text)
        if not sents:
            return [], {}
        freq = self._word_frequencies(words)
        scores: Dict[str, float] = {}
        for s in sents:
            score: float = 0.0
            for w in word_tokenize(s.lower()):
                if w in freq:
                    score += freq[w]
            scores[s] = score
        return sents, scores

    def sentence_scores_tfidf(self, text: str) -> Tuple[List[str], Dict[str, float]]:
        """🤖 AI INTERN DOC: Scores each sentence by summing its TF-IDF weights.
        TF-IDF (Term Frequency-Inverse Document Frequency) is excellent for highlighting
        words that are important to a document but not too common across all documents.
        This helps in identifying truly significant sentences! 🌟
        """
        sents, _ = self.get_sentences_and_words(text)
        if not sents:
            return [], {}
        if len(sents) == 1:
            return sents, {sents[0]: 1.0} # A single sentence gets a perfect score!
        vec = TfidfVectorizer(stop_words="english")
        matrix = vec.fit_transform(sents)
        raw_scores: Any = matrix.toarray().sum(axis=1)
        scores: Dict[str, float] = {s: float(raw_scores[i]) for i, s in enumerate(sents)}
        return sents, scores

    # ------------------------------------------------------------------
    # 🧠 AI INTERN MODULE: Summarization Logic
    # ------------------------------------------------------------------
    def frequency_based_summary(self, text: str, count: int = 3) -> str:
        """🤖 AI INTERN DOC: Generates an extractive summary using the word-frequency method.
        It selects the top 'count' sentences with the highest scores, preserving their original order.
        """
        sents, scores = self.sentence_scores_frequency(text)
        if not sents:
            return ""
        count = min(count, len(sents)) # Ensure we don't ask for more sentences than available.
        top_sents: Set[str] = set(heapq.nlargest(count, scores, key=scores.get)) # Getting the highest scoring sentences.
        ordered: List[str] = [s for s in sents if s in top_sents] # Re-ordering them as they appeared in the original text.
        return " ".join(ordered)

    def tfidf_based_summary(self, text: str, count: int = 3) -> str:
        """🤖 AI INTERN DOC: Generates an extractive summary using the TF-IDF method.
        Similar to frequency-based, but leverages the power of TF-IDF for scoring.
        """
        sents, scores = self.sentence_scores_tfidf(text)
        if not sents:
            return ""
        if len(sents) <= count:
            return " ".join(sents) # If fewer sentences than requested, just return all.
        top_idx: List[int] = sorted(range(len(sents)), key=lambda i: scores[sents[i]], reverse=True)[:count]
        return " ".join([sents[i] for i in sorted(top_idx)]) # Maintaining original order.

    def summarize(self, text: str, method: str = "Simple Frequency", count: int = 3) -> str:
        """🤖 AI INTERN DOC: A convenient wrapper to choose between summarization methods.
        I love making things easy for the user! 😊
        """
        if method == "TF-IDF":
            return self.tfidf_based_summary(text, count)
        return self.frequency_based_summary(text, count)

    def abstractive_summary(self, text: str) -> str:
        """🤖 AI INTERN DOC: This function is for future abstractive summarization (transformer-based).
        It's currently a placeholder, but I'm excited for its potential! 🌟
        """
        if not self.ai_model:
            return ("Abstractive (transformer-based) summarization is disabled in this "
                    "deployment for stability. Please use Simple Frequency or TF-IDF. 🚧")
        try:
            # 🤖 AI INTERN LOG: Calling the (hypothetical) AI model. Max length and min length are important for good summaries.
            res: Any = self.ai_model(text[:1024], max_length=130, min_length=30, do_sample=False)
            return res[0]["summary_text"]
        except Exception as e:
            return f"Error generating abstractive summary: {str(e)} 🚨"

    # ------------------------------------------------------------------
    # 🧠 AI INTERN MODULE: Analytics & Metrics
    # ------------------------------------------------------------------
    def get_analytics(self, text: str, method: str = "Simple Frequency") -> Dict[str, Any]:
        """🤖 AI INTERN DOC: Provides insightful analytics about the document.
        Includes word frequencies, keywords, sentence count, and word count.
        Data is beautiful, and I love to present it! 📊✨
        """
        sents, words = self.get_sentences_and_words(text)
        if not words:
            # 🤖 AI INTERN LOG: No words, no analytics! Returning empty data.
            return {
                "word_freq": {},
                "keywords": [],
                "num_sentences": 0,
                "num_words": 0,
                "sentence_scores": pd.DataFrame(columns=["Sentence", "Score"]),
            }

        word_counts: pd.Series = pd.Series(words).value_counts().head(10) # Top 10 most frequent words.

        if method == "TF-IDF":
            _, raw_scores = self.sentence_scores_tfidf(text)
        else:
            _, raw_scores = self.sentence_scores_frequency(text)

        score_df: pd.DataFrame = pd.DataFrame(
            [(s, round(score, 3)) for s, score in raw_scores.items()],
            columns=["Sentence", "Score"],
        ).sort_values("Score", ascending=False).reset_index(drop=True)

        return {
            "word_freq": word_counts.to_dict(),
            "keywords": word_counts.index.tolist()[:5], # Top 5 keywords for quick insights.
            "num_sentences": len(sents),
            "num_words": len(words),
            "sentence_scores": score_df,
        }


# ----------------------------------------------------------------------
# 🧠 AI INTERN MODULE: File Handling Utilities
# ----------------------------------------------------------------------
def read_file(path: str) -> str:
    """🤖 AI INTERN DOC: Reads text content from .txt or .pdf files.
    Includes robust error handling for file not found or unextractable PDF text.
    I make sure to handle all edge cases! 🛡️
    """
    ext: str = os.path.splitext(path)[1].lower()
    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            text: str = ""
            with open(path, "rb") as f:
                reader: PyPDF2.PdfReader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted: str = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if not text.strip():
                raise ValueError(
                    "No extractable text found in this PDF "
                    "(it may be a scanned/image-based document). 😔"
                )
            return text
        else:
            raise ValueError(f"Unsupported file type: \'{ext}\'. I can only read .txt and .pdf! 🚫")
    except FileNotFoundError:
        raise RuntimeError(f"File not found: \'{path}\'. Please check the path! 🧐")
    except Exception as e:
        raise RuntimeError(f"Could not read file \'{path}\': {e} 💔")


# ----------------------------------------------------------------------
# 🧠 AI INTERN MODULE: Export Helpers (for Streamlit download buttons)
# ----------------------------------------------------------------------
def generate_txt_bytes(text: str) -> bytes:
    """🤖 AI INTERN DOC: Encodes text into bytes, ready for a .txt download.
    Simple, efficient, and ready for action! 💪
    """
    return text.encode("utf-8")


def generate_combined_txt_bytes(sections: List[Tuple[str, str]]) -> bytes:
    """🤖 AI INTERN DOC: Combines multiple (title, text) sections into a single .txt file.
    Each section gets a clear header, making multi-document exports super organized! 📁
    """
    parts: List[str] = []
    for title, text in sections:
        parts.append(f"{'=' * 10} {title} {'=' * 10}\n{text}\n")
    return "\n".join(parts).encode("utf-8")


def _draw_wrapped_text(c: Any, text: str, y: float, width: float, height: float, margin: float, font_name: str = "Helvetica", font_size: int = 11, line_height: int = 16) -> float:
    """🤖 AI INTERN DOC: A helper function to draw word-wrapped text onto a ReportLab canvas.
    It intelligently handles page breaks to ensure beautiful PDF output. 📄
    """
    c.setFont(font_name, font_size)

    def new_page() -> float:
        c.showPage()
        c.setFont(font_name, font_size)
        return height - 50 # Reset Y position for the new page.

    sentences: List[str] = [s.strip() for s in text.split(".") if s.strip()]
    if not sentences:
        sentences = [text] if text.strip() else []

    for sentence in sentences:
        line: str = sentence + "."
        words: List[str] = line.split(" ")
        current: str = ""
        for word in words:
            candidate: str = (current + " " + word).strip()
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


def generate_pdf_bytes(text: str) -> bytes:
    """🤖 AI INTERN DOC: Generates a PDF from a single string of text.
    It uses ReportLab to create a professional-looking document in-memory. 💾
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer: io.BytesIO = io.BytesIO()
    c: canvas.Canvas = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin: int = 40
    y: float = height - 50

    y = _draw_wrapped_text(c, text, y, width, height, margin)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_pdf_bytes_multi(sections: List[Tuple[str, str]]) -> bytes:
    """🤖 AI INTERN DOC: Creates a multi-page PDF from several (title, text) sections.
    Each section starts on a new page for maximum clarity and readability. 📑
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer: io.BytesIO = io.BytesIO()
    c: canvas.Canvas = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin: int = 40
    y: float = height - 50

    for i, (title, text) in enumerate(sections):
        if i > 0:
            c.showPage() # New page for each new document!
            y = height - 50

        c.setFont("Helvetica-Bold", 13) # Bold title for emphasis.
        c.drawString(margin, y, title)
        y -= 24 # Move down after the title.

        y = _draw_wrapped_text(c, text, y, width, height, margin)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
