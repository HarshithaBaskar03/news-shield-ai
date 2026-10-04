import streamlit as st
import pickle
import re
import requests
import html
from urllib.parse import quote_plus, urlparse
from xml.etree import ElementTree as ET
from langdetect import detect
from translation import translate_to_english


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="News Shield AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html("""
<style>

:root {
    --ink: #f4fbff;
    --muted: #8ea6b4;
    --panel: rgba(13, 29, 42, 0.88);
    --panel-soft: rgba(10, 24, 36, 0.92);
    --line: rgba(121, 177, 198, 0.2);
    --teal: #55e0d0;
    --cyan: #67c8ff;
    --green: #5de39a;
    --red: #ff7185;
    --gold: #f7c969;
}

.stApp {
    background:
        linear-gradient(135deg, rgba(24, 77, 103, 0.16), transparent 36%),
        radial-gradient(circle at 92% 8%, rgba(85, 224, 208, 0.1), transparent 26rem),
        #06121d;
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: rgba(10, 23, 28, 0.88);
}

[data-testid="stToolbar"] {
    right: 1rem;
}

[data-testid="stDecoration"] {
    background-image: linear-gradient(90deg, var(--teal), var(--coral));
    height: 3px;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

.main-title {
    color: var(--ink);
    font-family: "Segoe UI", Inter, sans-serif;
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700;
    letter-spacing: 0.01em;
    line-height: 1.05;
    margin-bottom: 14px;
}

.subtitle {
    color: var(--muted);
    font-size: 1.05rem;
    line-height: 1.6;
    margin-bottom: 24px;
}

.stage {
    background: rgba(85, 224, 208, 0.07);
    border: 1px solid rgba(85, 224, 208, 0.18);
    border-radius: 10px;
    color: var(--ink);
    font-size: 0.96rem;
    letter-spacing: 0.02em;
    margin: 24px 0 12px;
    padding: 11px 15px;
}

.result-box {
    border-radius: 12px;
    margin-top: 20px;
    padding: 20px;
}

.section-card {
    background: linear-gradient(145deg, rgba(15, 38, 53, 0.92), rgba(8, 24, 37, 0.92));
    border: 1px solid var(--line);
    border-radius: 12px;
    box-shadow: 0 20px 55px rgba(0, 0, 0, 0.24);
    margin: 18px 0;
    padding: clamp(22px, 4vw, 42px);
}

.evidence-card {
    background: var(--panel-soft);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.16);
    margin: 14px 0;
    padding: 22px;
}

.final-card {
    background: linear-gradient(135deg, rgba(85, 224, 208, 0.16), rgba(8, 29, 43, 0.98));
    border: 1px solid rgba(85, 224, 208, 0.42);
    border-radius: 12px;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.24);
    margin: 18px 0;
    padding: 28px;
}

.footer-card {
    color: var(--muted);
    font-size: 0.88rem;
    padding: 34px 10px 8px;
    text-align: center;
}

h1, h2, h3, h4, p, li, label, [data-testid="stMarkdownContainer"] {
    color: var(--ink);
}

p, li {
    line-height: 1.7;
}

[data-testid="stTextArea"] textarea {
    background: #071722;
    border: 1px solid rgba(170, 205, 208, 0.24);
    border-radius: 10px;
    color: var(--ink);
    font-size: 1rem;
    line-height: 1.65;
    padding: 16px;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: var(--teal);
    box-shadow: 0 0 0 1px var(--teal), 0 0 24px rgba(83, 213, 193, 0.14);
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #6f888f;
}

[data-testid="stButton"] button {
    background: linear-gradient(135deg, var(--teal), #2aa9b6);
    border: 0;
    border-radius: 10px;
    color: #062126;
    font-size: 1rem;
    font-weight: 800;
    min-height: 3.1rem;
    transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}

[data-testid="stButton"] button:hover {
    box-shadow: 0 12px 28px rgba(83, 213, 193, 0.22);
    filter: brightness(1.08);
    transform: translateY(-2px);
}

[data-testid="stMetric"] {
    background: var(--panel-soft);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 18px;
}

[data-testid="stMetricLabel"] p {
    color: var(--muted);
}

[data-testid="stMetricValue"] {
    color: var(--teal);
}

[data-testid="stAlert"] {
    background: rgba(35, 31, 18, 0.92);
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--ink);
}

table th { border-bottom: 1px solid var(--line); color: var(--muted); font-size: .75rem; letter-spacing: .1em; padding: 10px 8px; }
table td { border-bottom: 1px solid rgba(121, 177, 198, 0.1); color: var(--ink); padding: 11px 8px; }
[data-testid="stExpander"] { background: rgba(13, 29, 42, 0.68); border: 1px solid var(--line); border-radius: 10px; }

a {
    color: var(--teal) !important;
    font-weight: 700;
    text-decoration-color: rgba(83, 213, 193, 0.4) !important;
}

.eyebrow { color: var(--teal); font-size: 0.74rem; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; }
.hero-meta { color: var(--muted); font-size: 0.92rem; margin-top: 18px; }
.badge { background: rgba(103, 200, 255, 0.09); border: 1px solid rgba(103, 200, 255, 0.2); border-radius: 999px; color: #b8e8ff; display: inline-block; font-size: 0.76rem; margin: 5px 5px 0 0; padding: 7px 11px; }
.result-label { color: var(--muted); font-size: 0.78rem; font-weight: 800; letter-spacing: 0.13em; text-transform: uppercase; }
.probability-track { background: #071722; border: 1px solid var(--line); border-radius: 99px; height: 12px; overflow: hidden; }
.probability-fill { background: linear-gradient(90deg, var(--red), #ffb06d); border-radius: inherit; height: 100%; }
.result-real .probability-fill { background: linear-gradient(90deg, var(--green), var(--teal)); }
.result-real .probability-fill { background: linear-gradient(90deg, var(--green), var(--teal)); }
.direction-supports { border-left: 3px solid var(--green); }
.direction-contradicts { border-left: 3px solid var(--red); }
.direction-unclear { border-left: 3px solid var(--gold); }
.muted { color: var(--muted); }

hr {
    border-color: var(--line);
    margin: 2.5rem 0;
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2rem;
    }

    .section-card {
        border-radius: 14px;
        padding: 22px;
    }

    .section-card > div[style*="grid-template-columns"] { grid-template-columns: repeat(2, 1fr) !important; }
}

</style>
""")


# ============================================================
# HEADER
# ============================================================

st.html("""
<div class="section-card">

<div class="eyebrow">AI FACT-CHECKING / EVIDENCE VERIFICATION</div>

<div class="main-title">
🛡️ NEWS SHIELD AI
</div>

<div class="subtitle">
AI-Powered Fake News Detection and Evidence Verification System
</div>

<div class="hero-meta">
<span class="badge">🌐 Multilingual Analysis</span>
<span class="badge">🔎 Explainable AI</span>
<span class="badge">🛡️ Evidence Verification</span>
</div>

</div>
""")


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

LANGUAGE_NAMES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "bn": "Bengali",
    "mr": "Marathi"
}


# ============================================================
# MODEL LOADING
# ============================================================

@st.cache_resource
def load_model():

    with open("random_forest_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open("tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    return model, vectorizer


try:

    model, vectorizer = load_model()

except Exception as e:

    st.error("❌ Unable to load the trained model files.")

    st.code(
        "Make sure these files are present in the same folder:\n\n"
        "random_forest_model.pkl\n"
        "tfidf_vectorizer.pkl"
    )

    st.stop()


# ============================================================
# TEXT PREPROCESSING
# ============================================================

def preprocess_text(text):

    text = str(text).lower()

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"[–—−]", "-", text)

    text = re.sub(r"[$₹€£]", " currency ", text)

    text = re.sub(r"%", " percent ", text)

    text = re.sub(r"[^a-z0-9.\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text):

    if not text.strip():
        return "en"

    english_words = {
        "the",
        "is",
        "are",
        "was",
        "were",
        "government",
        "india",
        "today",
        "announced",
        "news",
        "minister",
        "according",
        "official"
    }

    words = set(
        re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower()
        )
    )

    english_score = len(
        words.intersection(english_words)
    )

    if english_score >= 2:
        return "en"

    try:

        detected = detect(text)

        if detected in LANGUAGE_NAMES:
            return detected

    except Exception:
        pass

    return "en"


# ============================================================
# SENTENCE PROCESSING
# ============================================================

def split_into_sentences(text):

    text = re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# REPRESENTATIVE CLAIM SELECTION
# ============================================================

def select_representative_line(text):

    text = str(text).strip()

    if not text:
        return ""

    sentences = split_into_sentences(text)

    if not sentences:
        return text

    # Preserve the complete input when it is already a single factual
    # statement. This prevents claim-critical details at the beginning
    # of a sentence from being lost during representative-line selection.
    if len(sentences) == 1:
        return sentences[0]

    factual_keywords = [
        "government",
        "minister",
        "ministry",
        "announced",
        "approved",
        "launched",
        "introduced",
        "policy",
        "scheme",
        "decision",
        "according",
        "official",
        "india",
        "court",
        "company",
        "price",
        "election",
        "education",
        "health",
        "economy",
        "president",
        "prime",
        "rbi",
        "upi",
        "defence",
        "defense"
    ]

    best_sentence = sentences[0]
    best_score = -1

    for sentence in sentences:

        lower = sentence.lower()

        score = sum(
            1
            for word in factual_keywords
            if word in lower
        )

        score += min(
            len(sentence.split()) / 50,
            2
        )

        if score > best_score:

            best_score = score
            best_sentence = sentence

    return best_sentence


# ============================================================
# SIMILARITY HELPERS
# ============================================================

GENERIC_TERMS = {
    "india",
    "indian",
    "government",
    "official",
    "officials",
    "news",
    "report",
    "reports",
    "according",
    "today",
    "latest",
    "new",
    "people",
    "country",
    "state",
    "national",
    "minister",
    "ministry",
    "said",
    "says"
}


STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "from",
    "with",
    "and",
    "or",
    "but",
    "as",
    "by",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "their",
    "his",
    "her",
    "they",
    "them",
    "he",
    "she",
    "will",
    "would",
    "should",
    "could",
    "has",
    "have",
    "had",
    "said"
}


def normalize_for_similarity(text):

    text = html.unescape(
        str(text)
    ).lower()

    text = re.sub(
        r"https?://\S+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    words = re.findall(
        r"\b[a-z0-9]{2,}\b",
        text
    )

    return set(words)


def get_claim_specific_terms(claim):

    words = normalize_for_similarity(
        claim
    )

    return {
        word
        for word in words
        if (
            word not in GENERIC_TERMS
            and word not in STOPWORDS
        )
    }


def calculate_claim_relevance(
    claim,
    evidence
):

    claim_words = normalize_for_similarity(
        claim
    )

    evidence_words = normalize_for_similarity(
        evidence
    )

    if not claim_words:
        return 0.0

    overlap = len(
        claim_words.intersection(
            evidence_words
        )
    )

    return min(
        overlap / len(claim_words),
        1.0
    )


def count_specific_overlap(
    claim,
    evidence
):

    specific_terms = get_claim_specific_terms(
        claim
    )

    evidence_words = normalize_for_similarity(
        evidence
    )

    return len(
        specific_terms.intersection(
            evidence_words
        )
    )


# ============================================================
# SOURCE AUTHORITY
# ============================================================

TIER_1_DOMAINS = {
    "gov.in",
    "nic.in",
    "pib.gov.in",
    "education.gov.in",
    "mha.gov.in",
    "mohfw.gov.in",
    "mea.gov.in",
    "rbi.org.in",
    "eci.gov.in",
    "isro.gov.in",
    "upsc.gov.in",
    "nta.ac.in"
}


TIER_2_DOMAINS = {
    "reuters.com",
    "bbc.com",
    "bbc.co.uk",
    "thehindu.com",
    "thehindubusinessline.com",
    "indianexpress.com",
    "hindustantimes.com",
    "ndtv.com",
    "timesofindia.indiatimes.com",
    "theprint.in",
    "deccanherald.com",
    "news18.com",
    "business-standard.com",
    "economictimes.indiatimes.com",
    "financialexpress.com"
}


PUBLISHER_DOMAIN_MAP = {

    # --------------------------------------------------------
    # OFFICIAL / GOVERNMENT SOURCES
    # --------------------------------------------------------

    "pib": "pib.gov.in",

    "press information bureau": "pib.gov.in",

    "pm india": "pmindia.gov.in",

    "pmindia": "pmindia.gov.in",

    "prime minister's office": "pmindia.gov.in",

    "prime ministers office": "pmindia.gov.in",

    "rbi": "rbi.org.in",

    "reserve bank of india": "rbi.org.in",

    "election commission of india": "eci.gov.in",

    "election commission": "eci.gov.in",

    "isro": "isro.gov.in",

    "nta": "nta.ac.in",

    "upsc": "upsc.gov.in",

    "ministry of education": "education.gov.in",

    "ministry of home affairs": "mha.gov.in",

    "ministry of health": "mohfw.gov.in",

    "ministry of external affairs": "mea.gov.in",

    # --------------------------------------------------------
    # ESTABLISHED NEWS SOURCES
    # --------------------------------------------------------

    "reuters": "reuters.com",

    "bbc": "bbc.com",

    "the hindu": "thehindu.com",

    "business line": "thehindubusinessline.com",

    "the hindu business line":
        "thehindubusinessline.com",

    "businessline":
        "thehindubusinessline.com",

    "indian express":
        "indianexpress.com",

    "hindustan times":
        "hindustantimes.com",

    "ndtv":
        "ndtv.com",

    "times of india":
        "timesofindia.indiatimes.com",

    "the print":
        "theprint.in",

    "deccan herald":
        "deccanherald.com",

    "news18":
        "news18.com",

    "business standard":
        "business-standard.com",

    "economic times":
        "economictimes.indiatimes.com",

    "financial express":
        "financialexpress.com"
}


def get_domain(url):

    try:

        domain = urlparse(
            url
        ).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:

        return ""


def get_source_authority(
    url,
    publisher=""
):

    domain = get_domain(url)

    publisher_lower = str(
        publisher
    ).lower().strip()

    # --------------------------------------------------------
    # 1. OFFICIAL PUBLISHER RECOGNITION
    # --------------------------------------------------------
    #
    # Google News RSS often gives a Google News URL such as:
    #
    # news.google.com/rss/articles/...
    #
    # In that case, the URL domain itself is NOT the real
    # publisher domain.
    #
    # Therefore, official publisher names must be checked
    # before classifying the Google News URL.
    #

    official_publisher_aliases = {

        "pib": "pib.gov.in",

        "press information bureau":
            "pib.gov.in",

        "pm india":
            "pmindia.gov.in",

        "pmindia":
            "pmindia.gov.in",

        "prime minister's office":
            "pmindia.gov.in",

        "prime ministers office":
            "pmindia.gov.in",

        "rbi":
            "rbi.org.in",

        "reserve bank of india":
            "rbi.org.in",

        "election commission of india":
            "eci.gov.in",

        "election commission":
            "eci.gov.in",

        "isro":
            "isro.gov.in",

        "upsc":
            "upsc.gov.in",

        "nta":
            "nta.ac.in",

        "ministry of education":
            "education.gov.in",

        "ministry of home affairs":
            "mha.gov.in",

        "ministry of health":
            "mohfw.gov.in",

        "ministry of external affairs":
            "mea.gov.in"
    }

    # Exact / clear official publisher recognition.
    for publisher_name, official_domain in (
        official_publisher_aliases.items()
    ):

        if (
            publisher_lower == publisher_name
            or publisher_name in publisher_lower
        ):

            return 1, official_domain

    # --------------------------------------------------------
    # 2. OFFICIAL URL DOMAIN RECOGNITION
    # --------------------------------------------------------

    for official_domain in TIER_1_DOMAINS:

        if (
            domain == official_domain
            or domain.endswith(
                "." + official_domain
            )
        ):

            return 1, official_domain

    # --------------------------------------------------------
    # 3. ESTABLISHED NEWS URL DOMAIN RECOGNITION
    # --------------------------------------------------------

    for established_domain in TIER_2_DOMAINS:

        if (
            domain == established_domain
            or domain.endswith(
                "." + established_domain
            )
        ):

            return 2, established_domain

    # --------------------------------------------------------
    # 4. ESTABLISHED NEWS PUBLISHER RECOGNITION
    # --------------------------------------------------------

    for publisher_name, mapped_domain in (
        PUBLISHER_DOMAIN_MAP.items()
    ):

        # Do not let official publisher mappings fall into
        # Tier 2. They have already been handled above.
        if mapped_domain in TIER_1_DOMAINS:
            continue

        if publisher_name in publisher_lower:

            return 2, mapped_domain

    # --------------------------------------------------------
    # 5. UNKNOWN / OTHER SOURCE
    # --------------------------------------------------------

    return 3, domain


# ============================================================
# DATE FUNCTIONS
# ============================================================

def _normalize_date_piece(value):
    return re.sub(r"\s+", " ", str(value).strip().lower())


MONTH_NUMBERS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}


def _canonicalize_date(date_text):
    value = _normalize_date_piece(date_text)
    value = value.replace(",", "")

    # Numeric dates
    match = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", value)
    if match:
        day, month, year = match.groups()
        year = int(year)
        if year < 100:
            year += 2000
        return f"{year:04d}-{int(month):02d}-{int(day):02d}"

    match = re.fullmatch(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", value)
    if match:
        year, month, day = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

    # Month + day + year
    match = re.fullmatch(
        r"(jan|january|feb|february|mar|march|apr|april|may|"
        r"jun|june|jul|july|aug|august|sep|sept|september|"
        r"oct|october|nov|november|dec|december)\s+"
        r"(\d{1,2})\s+(\d{4})",
        value,
        flags=re.IGNORECASE
    )
    if match:
        month, day, year = match.groups()
        return f"{int(year):04d}-{MONTH_NUMBERS[month.lower()]:02d}-{int(day):02d}"

    # Day + month + year
    match = re.fullmatch(
        r"(\d{1,2})\s+"
        r"(jan|january|feb|february|mar|march|apr|april|may|"
        r"jun|june|jul|july|aug|august|sep|sept|september|"
        r"oct|october|nov|november|dec|december)\s+"
        r"(\d{4})",
        value,
        flags=re.IGNORECASE
    )
    if match:
        day, month, year = match.groups()
        return f"{int(year):04d}-{MONTH_NUMBERS[month.lower()]:02d}-{int(day):02d}"

    # Month + year
    match = re.fullmatch(
        r"(jan|january|feb|february|mar|march|apr|april|may|"
        r"jun|june|jul|july|aug|august|sep|sept|september|"
        r"oct|october|nov|november|dec|december)\s+(\d{4})",
        value,
        flags=re.IGNORECASE
    )
    if match:
        month, year = match.groups()
        return f"{int(year):04d}-{MONTH_NUMBERS[month.lower()]:02d}"

    # Month + day without year, e.g. "October 31" -> "10-31".
    match = re.fullmatch(
        r"(jan|january|feb|february|mar|march|apr|april|may|"
        r"jun|june|jul|july|aug|august|sep|sept|september|"
        r"oct|october|nov|november|dec|december)\s+(\d{1,2})",
        value,
        flags=re.IGNORECASE
    )
    if match:
        month, day = match.groups()
        return f"{MONTH_NUMBERS[month.lower()]:02d}-{int(day):02d}"

    # Day + month without year, e.g. "31 October" -> "10-31".
    match = re.fullmatch(
        r"(\d{1,2})\s+"
        r"(jan|january|feb|february|mar|march|apr|april|may|"
        r"jun|june|jul|july|aug|august|sep|sept|september|"
        r"oct|october|nov|november|dec|december)",
        value,
        flags=re.IGNORECASE
    )
    if match:
        day, month = match.groups()
        return f"{MONTH_NUMBERS[month.lower()]:02d}-{int(day):02d}"

    return value


def _date_month_key(canonical_date):
    parts = canonical_date.split("-")
    if len(parts) >= 2:
        return "-".join(parts[:2])
    return canonical_date


def extract_dates(text):
    """
    Extract explicit event dates without treating a source publication date
    as evidence. The caller supplies claim/evidence text, not RSS pubDate.
    Supports full dates and month-year expressions.
    """
    text = html.unescape(str(text))
    dates = []

    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
        r"\b(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|"
        r"Oct|October|Nov|November|Dec|December)"
        r"\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}\s+"
        r"(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|"
        r"Oct|October|Nov|November|Dec|December)"
        r"\s+\d{4}\b",
        r"\b(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|"
        r"Oct|October|Nov|November|Dec|December)"
        r"\s+\d{4}\b",

        # Month + day without year, e.g. "October 31"
        r"\b(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|"
        r"Oct|October|Nov|November|Dec|December)"
        r"\s+\d{1,2}\b",

        # Day + month without year, e.g. "31 October"
        r"\b\d{1,2}\s+"
        r"(?:Jan|January|Feb|February|Mar|March|Apr|April|"
        r"May|Jun|June|Jul|July|Aug|August|Sep|Sept|September|"
        r"Oct|October|Nov|November|Dec|December)\b"
    ]

    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            canonical = _canonicalize_date(match)
            if canonical not in dates:
                dates.append(canonical)

    return dates


def format_date(date_text):
    return str(date_text).strip()


def check_date_consistency(claim, evidence):
    claim_dates = extract_dates(claim)
    evidence_dates = extract_dates(evidence)

    if not claim_dates or not evidence_dates:
        return {
            "status": "unknown",
            "claim_dates": claim_dates,
            "evidence_dates": evidence_dates
        }

    claim_set = set(claim_dates)
    evidence_set = set(evidence_dates)

    # Exact agreement, including exact year when both sides provide it.
    if claim_set.intersection(evidence_set):
        return {
            "status": "match",
            "claim_dates": claim_dates,
            "evidence_dates": evidence_dates
        }

    # Compare year-less month/day values (MM-DD) against full dates.
    # This catches cases such as the claim saying October 30 while an
    # evidence headline says October 31 without repeating the year.
    claim_full_dates = {
        value for value in claim_dates
        if len(value.split("-")) == 3
    }
    evidence_full_dates = {
        value for value in evidence_dates
        if len(value.split("-")) == 3
    }

    claim_partial_dates = {
        value for value in claim_dates
        if len(value.split("-")) == 2
    }
    evidence_partial_dates = {
        value for value in evidence_dates
        if len(value.split("-")) == 2
    }

    claim_day_months = {
        "-".join(value.split("-")[1:])
        for value in claim_full_dates
    }
    evidence_day_months = {
        "-".join(value.split("-")[1:])
        for value in evidence_full_dates
    }

    if claim_full_dates and evidence_partial_dates:
        return {
            "status": "match" if claim_day_months.intersection(evidence_partial_dates)
            else "date_mismatch",
            "claim_dates": claim_dates,
            "evidence_dates": evidence_dates
        }

    if evidence_full_dates and claim_partial_dates:
        return {
            "status": "match" if evidence_day_months.intersection(claim_partial_dates)
            else "date_mismatch",
            "claim_dates": claim_dates,
            "evidence_dates": evidence_dates
        }

    # Both sides contain full dates but the days differ.
    if claim_full_dates and evidence_full_dates:
        return {
            "status": "date_mismatch",
            "claim_dates": claim_dates,
            "evidence_dates": evidence_dates
        }

    # Month-year compatibility remains allowed when one side genuinely
    # contains only month/year information.
    claim_months = {_date_month_key(value) for value in claim_dates}
    evidence_months = {_date_month_key(value) for value in evidence_dates}

    if claim_months.intersection(evidence_months):
        return {
            "status": "month_match",
            "claim_dates": claim_dates,
            "evidence_dates": evidence_dates
        }

    return {
        "status": "date_mismatch",
        "claim_dates": claim_dates,
        "evidence_dates": evidence_dates
    }


def _has_event_date_context(text):
    event_patterns = [
        r"\b(?:until|till|through|by|from|starting(?:\s+from)?|"
        r"effective(?:\s+from|\s+on)?|valid(?:\s+until|\s+till|\s+from)?|"
        r"extended(?:\s+until|\s+till|\s+through)?|"
        r"on|approved(?:\s+on)?|announced(?:\s+on)?|"
        r"issued(?:\s+on)?|launched(?:\s+on)?|introduced(?:\s+on)?|"
        r"started(?:\s+on)?|began(?:\s+on)?|available(?:\s+from|\s+on)?)\b"
    ]
    return any(re.search(pattern, text, flags=re.IGNORECASE)
               for pattern in event_patterns)


def _has_strong_contradiction_language(text):
    patterns = [
        r"\b(?:claim|claims|report|reports|rumou?r|post|message|statement|news)\b"
        r".{0,80}\b(?:false|fake|fabricated|hoax|misleading|incorrect|untrue|"
        r"debunked|debunk|not true|not correct|not accurate)\b",

        r"\b(?:false|fake|fabricated|hoax|misleading|incorrect|untrue)\b"
        r".{0,80}\b(?:claim|claims|report|reports|rumou?r|post|message|statement|news)\b",

        r"\b(?:government|ministry|officials?|rbi|police|court|company)\b"
        r".{0,80}\b(?:denied|denies|rejected|dismissed|clarified|clarification)\b",

        r"\b(?:no such|not announced|not approved|not confirmed|not extended|"
        r"not launched|not introduced|not issued|never happened|no evidence)\b"
    ]

    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def _has_support_language(text):
    patterns = [
        r"\bofficially announced\b",
        r"\bofficial announcement\b",
        r"\bofficial notification\b",
        r"\bofficial circular\b",
        r"\bofficial statement\b",
        r"\bconfirmed(?: by)?\b",
        r"\bannounced\b",
        r"\bannounces\b",
        r"\bstated\b",
        r"\bstates\b",
        r"\bissued\b",
        r"\bnotification\b",
        r"\bcircular\b",
        r"\bapproved\b",
        r"\bextended\b",
        r"\bextends\b",
        r"\blaunched\b",
        r"\blaunches\b",
        r"\bimplemented\b",
        r"\breleased\b",
        r"\bunveiled\b",
        r"\bintroduced\b",
        r"\baccording to\b",
        r"\bgovernment said\b",
        r"\bministry said\b",
        r"\bofficials said\b"
    ]

    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def determine_evidence_direction(claim, evidence_text, tier=3):
    """
    Classify one evidence item as supports / contradicts / unclear.

    The important rule is that evidence does not have to repeat a
    date word-for-word to support a claim. A date mismatch becomes
    contradiction only when the evidence explicitly presents a
    different event/deadline/effective date and the factual topic
    overlaps strongly.
    """
    claim = html.unescape(str(claim)).strip()
    text = html.unescape(str(evidence_text)).lower().strip()

    if not text:
        return "unclear"

    date_info = check_date_consistency(claim, text)
    claim_dates = date_info.get("claim_dates", [])
    evidence_dates = date_info.get("evidence_dates", [])
    date_status = date_info.get("status", "unknown")

    claim_words = normalize_for_similarity(claim)
    evidence_words = normalize_for_similarity(text)
    specific_terms = get_claim_specific_terms(claim)

    specific_overlap = len(
        specific_terms.intersection(evidence_words)
    )

    token_overlap = (
        len(claim_words.intersection(evidence_words)) / len(claim_words)
        if claim_words else 0.0
    )

    overlap_ratio = (
        specific_overlap / len(specific_terms)
        if specific_terms else 0.0
    )

    # Numeric values are useful only as supporting detail; the absence
    # of the same number is not automatically a contradiction.
    claim_numbers = set(
        re.findall(r"\b\d+(?:\.\d+)?\b", claim)
    )
    evidence_numbers = set(
        re.findall(r"\b\d+(?:\.\d+)?\b", text)
    )
    numeric_overlap = len(
        claim_numbers.intersection(evidence_numbers)
    )

    strong_topic_match = (
        specific_overlap >= 3
        and (
            overlap_ratio >= 0.40
            or token_overlap >= 0.45
        )
    )

    very_strong_topic_match = (
        specific_overlap >= 4
        and (
            overlap_ratio >= 0.55
            or token_overlap >= 0.60
        )
    )

    # --------------------------------------------------------
    # EXPLICIT CONTRADICTION
    # --------------------------------------------------------

    contradiction_language = _has_strong_contradiction_language(text)

    legal_tender_claim = (
        "cease to be legal tender" in claim.lower()
        or "no longer be legal tender" in claim.lower()
        or "become invalid" in claim.lower()
        or "will be invalid" in claim.lower()
        or "withdrawn from circulation" in claim.lower()
    )

    legal_tender_evidence = (
        "remain legal tender" in text
        or "remains legal tender" in text
        or "continues to be legal tender" in text
        or "continue to be legal tender" in text
    )

    legal_tender_contradiction = (
        legal_tender_claim
        and legal_tender_evidence
        and (
            specific_overlap >= 2
            or token_overlap >= 0.25
        )
    )

    # A different explicit deadline/effective date is a real
    # contradiction, not merely "unclear".
    date_event_contradiction = (
        date_status == "date_mismatch"
        and bool(claim_dates)
        and bool(evidence_dates)
        and _has_event_date_context(text)
        and specific_overlap >= 4
        and (
            "until" in text
            or "till" in text
            or "valid" in text
            or "effective" in text
            or "extended" in text
            or "from" in text
            or "starting" in text
            or "by" in text
            or "on" in text
        )
    )

    # Negative event wording such as "not approved", "not launched",
    # "denied", etc. can contradict a positive claim when the topic
    # itself is strongly aligned.
    negative_event_contradiction = (
        contradiction_language
        and (
            strong_topic_match
            or very_strong_topic_match
            or specific_overlap >= 2
            or token_overlap >= 0.30
        )
    )

    if (
        legal_tender_contradiction
        or date_event_contradiction
        or negative_event_contradiction
    ):
        return "contradicts"

    # --------------------------------------------------------
    # DIRECT / STRONG SUPPORT
    # --------------------------------------------------------

    exact_or_near_match = (
        len(claim_words) >= 4
        and token_overlap >= 0.75
    )

    # Exact or near-exact text from an authoritative source is strong
    # support, unless a contradiction was detected above.
    if exact_or_near_match and tier in {1, 2}:
        return "supports"

    # A same-month date is compatible. An evidence article with no
    # event date can still support the claim when the factual content
    # is strong; this is the key correction over the old logic.
        # --------------------------------------------------------
    # DATE-CRITICAL CLAIM PROTECTION
    # --------------------------------------------------------
    # If the claim contains a specific event date/deadline but the
    # evidence does not mention any event date, do NOT treat a
    # generic article about the same topic as direct support.
    #
    # Example:
    # Claim: "NMMSS deadline has been extended to October 30, 2026."
    #
    # Evidence:
    # "Registrations Open For National Means-Cum-Merit Scholarship
    # Scheme..." 
    #
    # This article may discuss the same scheme, but unless it
    # confirms the claimed deadline, it must remain UNCLEAR.
    #
    # This prevents generic topic overlap from overriding a
    # date-specific claim.

    claim_has_specific_date = any(
        len(value.split("-")) in {2, 3}
        for value in claim_dates
    )

    evidence_has_specific_date = any(
        len(value.split("-")) in {2, 3}
        for value in evidence_dates
    )

    date_compatible = date_status in {
        "unknown",
        "match",
        "month_match"
    }

    if not date_compatible:
        # A genuine event-date mismatch is handled above as
        # CONTRADICTS when sufficient topic/event overlap exists.
        if tier in {1, 2} and very_strong_topic_match:
            return "unclear"
        return "unclear"

    # A claim containing a specific date/deadline requires the
    # evidence to contain a compatible event date before it can
    # be classified as direct support.
    #
    # This is intentionally applied only to date-specific claims.
    # It does NOT affect ordinary claims without dates.
    if (
        claim_has_specific_date
        and not evidence_has_specific_date
        and specific_overlap >= 3
    ):
        return "unclear"

    # Strong factual match. Numeric overlap is helpful but not mandatory:
    # many authoritative articles describe the same event without
    # repeating every number from the claim.
    if tier in {1, 2} and very_strong_topic_match:
        return "supports"

    if (
        tier in {1, 2}
        and specific_overlap >= 3
        and overlap_ratio >= 0.40
    ):
        return "supports"

    # Support language can strengthen a high-quality factual match,
    # but language alone never proves the claim.
    if (
        tier in {1, 2}
        and _has_support_language(text)
        and specific_overlap >= 2
        and (
            overlap_ratio >= 0.35
            or token_overlap >= 0.40
        )
    ):
        return "supports"

    # Official sources receive a modest allowance because government
    # pages may use different wording while referring to the same event.
    if (
        tier == 1
        and specific_overlap >= 2
        and (
            overlap_ratio >= 0.35
            or token_overlap >= 0.35
        )
    ):
        return "supports"

    return "unclear"


# ============================================================
# GOOGLE FACT CHECK API
# ============================================================

def search_fact_check(claim):

    try:

        api_key = st.secrets.get(
            "GOOGLE_FACTCHECK_API_KEY",
            ""
        )

    except Exception:

        api_key = ""

    if not api_key:
        return []

    endpoint = (
        "https://factchecktools.googleapis.com/"
        "v1alpha1/claims:search"
    )

    params = {
        "query": claim,
        "key": api_key,
        "pageSize": 10
    }

    try:

        response = requests.get(
            endpoint,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        claims = data.get(
            "claims",
            []
        )

        results = []

        for item in claims:

            text = item.get(
                "text",
                ""
            )

            relevance = calculate_claim_relevance(
                claim,
                text
            )

            if relevance < 0.20:
                continue

            reviews = item.get(
                "claimReview",
                []
            )

            for review in reviews:

                rating = review.get(
                    "textualRating",
                    ""
                )

                publisher = review.get(
                    "publisher",
                    {}
                ).get(
                    "name",
                    "Unknown"
                )

                url = review.get(
                    "url",
                    ""
                )

                results.append({

                    "claim": text,

                    "rating": rating,

                    "publisher": publisher,

                    "url": url,

                    "relevance": relevance
                })

        results.sort(
            key=lambda x: x.get(
                "relevance",
                0
            ),
            reverse=True
        )

        return results[:10]

    except Exception:

        return []


# ============================================================
# GOOGLE NEWS RSS
# ============================================================

def fetch_google_news_rss(
    query,
    claim
):

    encoded_query = quote_plus(
        query
    )

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}"
        "&hl=en-IN&gl=IN&ceid=IN:en"
    )

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
            },
            timeout=12
        )

        if response.status_code != 200:
            return []

        root = ET.fromstring(
            response.content
        )

        results = []

        for item in root.findall(
            ".//item"
        ):

            title = item.findtext(
                "title",
                ""
            )

            link = item.findtext(
                "link",
                ""
            )

            description = item.findtext(
                "description",
                ""
            )

            pub_date = item.findtext(
                "pubDate",
                ""
            )

            source_element = item.find(
                "source"
            )

            publisher = ""

            if source_element is not None:

                publisher = (
                    source_element.text
                    or ""
                )

                source_url = source_element.get(
                    "url",
                    ""
                )

                if not link and source_url:
                    link = source_url

            combined_text = (
                f"{title} "
                f"{description}"
            )

            relevance = calculate_claim_relevance(
                claim,
                combined_text
            )

            overlap = count_specific_overlap(
                claim,
                combined_text
            )

            tier, recognized_domain = (
                get_source_authority(
                    link,
                    publisher
                )
            )

            direction = determine_evidence_direction(
                claim,
                combined_text,
                tier
            )

            results.append({

                "title": html.unescape(
                    title
                ),

                "link": link,

                "publisher": publisher,

                "domain": recognized_domain,

                "tier": tier,

                "relevance": relevance,

                "specific_overlap": overlap,

                "direction": direction,

                "description": html.unescape(
                    description
                ),

                "published": pub_date
            })

        return results

    except Exception:

        return []


# ============================================================
# SEARCH QUERY BUILDING
# ============================================================

def build_search_queries(claim):

    queries = []

    clean_claim = re.sub(
        r"\s+",
        " ",
        claim
    ).strip()

    # --------------------------------------------------------
    # Exact claim
    # --------------------------------------------------------

    queries.append(
        f'"{clean_claim}"'
    )

    # --------------------------------------------------------
    # Build meaningful claim terms
    # --------------------------------------------------------

    specific_terms = list(
        get_claim_specific_terms(
            clean_claim
        )
    )

    # Keep terms that are likely to identify
    # the actual event/person/topic.
    important_terms = [
        term
        for term in specific_terms
        if len(term) >= 4
    ]

    # Limit query complexity
    important_terms = important_terms[:8]

    if important_terms:

        # Main keyword query
        queries.append(
            " ".join(
                important_terms[:5]
            )
        )

        # First group
        if len(important_terms) >= 3:

            queries.append(
                " ".join(
                    important_terms[:3]
                )
            )

        # Second group
        if len(important_terms) >= 5:

            queries.append(
                " ".join(
                    important_terms[2:6]
                )
            )

    # --------------------------------------------------------
    # Named entities / important terms
    # --------------------------------------------------------

    entity_patterns = [
        r"\bPrime Minister\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*",
        r"\bPresident\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*",
        r"\b[A-Z][A-Za-z]+\s+(?:UPI|RBI|IPO)\b"
    ]

    entities = []

    for pattern in entity_patterns:

        matches = re.findall(
            pattern,
            clean_claim
        )

        entities.extend(
            matches
        )

    for entity in entities[:3]:

        queries.append(
            entity
        )

        queries.append(
            f'"{entity}"'
        )

    # --------------------------------------------------------
    # Official sources
    # --------------------------------------------------------

    queries.extend([

        f'site:pib.gov.in {clean_claim}',

        f'site:gov.in {clean_claim}',

        f'site:nic.in {clean_claim}',

        f'site:rbi.org.in {clean_claim}',

        f'site:mea.gov.in {clean_claim}'
    ])

    # --------------------------------------------------------
    # Established news sources
    # --------------------------------------------------------

    queries.extend([

        f'site:reuters.com {clean_claim}',

        f'site:bbc.com {clean_claim}',

        f'site:thehindu.com {clean_claim}',

        f'site:indianexpress.com {clean_claim}',

        f'site:hindustantimes.com {clean_claim}',

        f'site:ndtv.com {clean_claim}',

        f'site:business-standard.com {clean_claim}',

        f'site:economictimes.indiatimes.com {clean_claim}'
    ])

    # --------------------------------------------------------
    # Contradiction searches
    # --------------------------------------------------------

    contradiction_terms = [
        "false",
        "fake",
        "debunked",
        "misleading",
        "fact check",
        "denied",
        "clarification"
    ]

    for term in contradiction_terms:

        if important_terms:

            queries.append(
                f'{" ".join(important_terms[:5])} {term}'
            )

        else:

            queries.append(
                f'"{clean_claim}" {term}'
            )

    # --------------------------------------------------------
    # General claim
    # --------------------------------------------------------

    queries.append(
        clean_claim
    )

    # Remove duplicates while preserving order

    unique_queries = []

    seen = set()

    for query in queries:

        normalized = query.lower().strip()

        if (
            normalized
            and normalized not in seen
        ):

            seen.add(
                normalized
            )

            unique_queries.append(
                query
            )

    return unique_queries[:30]


# ============================================================
# GOOGLE NEWS SEARCH
# ============================================================

def search_google_news(claim):

    all_results = []

    queries = build_search_queries(
        claim
    )

    for query in queries:

        results = fetch_google_news_rss(
            query,
            claim
        )

        all_results.extend(
            results
        )

    # --------------------------------------------------------
    # Deduplication
    # --------------------------------------------------------

    unique = {}

    for result in all_results:

        title_key = re.sub(
            r"[^a-z0-9]",
            "",
            result.get(
                "title",
                ""
            ).lower()
        )

        publisher_key = re.sub(
            r"[^a-z0-9]",
            "",
            result.get(
                "publisher",
                ""
            ).lower()
        )

        key = (
            title_key,
            publisher_key
        )

        if key not in unique:

            unique[key] = result

        else:

            existing = unique[key]

            if (
                result.get(
                    "relevance",
                    0
                )
                >
                existing.get(
                    "relevance",
                    0
                )
            ):

                unique[key] = result

    # --------------------------------------------------------
    # Re-score and filter
    # --------------------------------------------------------

    filtered = []

    claim_words = normalize_for_similarity(
        claim
    )

    specific_terms = get_claim_specific_terms(
        claim
    )

    for result in unique.values():

        title = result.get(
            "title",
            ""
        )

        description = result.get(
            "description",
            ""
        )

        publisher = result.get(
            "publisher",
            ""
        )

        combined = (
            title
            + " "
            + description
        )

        relevance = calculate_claim_relevance(
            claim,
            combined
        )

        overlap = count_specific_overlap(
            claim,
            combined
        )

        tier, recognized_domain = (
            get_source_authority(
                result.get(
                    "link",
                    ""
                ),
                publisher
            )
        )

        title_words = normalize_for_similarity(
            title
        )

        if claim_words:

            title_overlap = (
                len(
                    claim_words.intersection(
                        title_words
                    )
                )
                / len(claim_words)
            )

        else:

            title_overlap = 0.0

        # ----------------------------------------------------
        # Source-specific relaxed filtering
        # ----------------------------------------------------

        keep = False

        # Official source
        if tier == 1:

            if (
                relevance >= 0.25
                and overlap >= 2
            ):

                keep = True

            elif (
                title_overlap >= 0.30
                and overlap >= 2
            ):

                keep = True

        # Established source
        elif tier == 2:

            if (
                relevance >= 0.25
                and overlap >= 2
            ):

                keep = True

            elif (
                title_overlap >= 0.25
                and overlap >= 2
            ):

                keep = True

            elif (
                relevance >= 0.18
                and overlap >= 3
            ):

                keep = True

        # Other source
        else:

            if (
                relevance >= 0.45
                and overlap >= 3
            ):

                keep = True

        if not keep:
            continue

        result["relevance"] = relevance

        result["specific_overlap"] = overlap

        result["tier"] = tier

        result["domain"] = recognized_domain

        result["direction"] = (
            determine_evidence_direction(
                claim,
                combined,
                tier
            )
        )

        result["title_overlap"] = (
            title_overlap
        )

        filtered.append(
            result
        )

    # --------------------------------------------------------
    # Sort results
    # --------------------------------------------------------

    direction_priority = {
        "supports": 0,
        "contradicts": 1,
        "unclear": 2
    }

    filtered.sort(
        key=lambda x: (
            x.get("tier", 3),

            direction_priority.get(
                x.get(
                    "direction",
                    "unclear"
                ),
                2
            ),

            -x.get(
                "specific_overlap",
                0
            ),

            -x.get(
                "relevance",
                0.0
            )
        )
    )

    return filtered[:12]


# ============================================================
# AUTHORITATIVE EVIDENCE ASSESSMENT
# ============================================================

def assess_authoritative_evidence(
    results
):
    """
    Count only sufficiently strong authoritative evidence.

    Tier 1: one strong official/institutional source can establish
            a direction when relevance and claim-specific overlap
            are both adequate.

    Tier 2: normally require two strong sources, unless one source
            is exceptionally relevant and specific.

    If strong support and strong contradiction both exist, the result
    is deliberately marked conflicting so the ML result is retained.
    """

    support_signals = 0
    contradiction_signals = 0

    for result in results:
        tier = result.get("tier", 3)
        relevance = float(result.get("relevance", 0.0) or 0.0)
        direction = result.get("direction", "unclear")
        overlap = int(result.get("specific_overlap", 0) or 0)

        if direction not in {"supports", "contradicts"}:
            continue

        if tier == 1:
            strong_signal = (
                relevance >= 0.25 and overlap >= 2
            ) or (
                overlap >= 3 and relevance >= 0.20
            )

        elif tier == 2:
            strong_signal = (
                relevance >= 0.30 and overlap >= 3
            ) or (
                relevance >= 0.40 and overlap >= 2
            )

        else:
            strong_signal = False

        if not strong_signal:
            continue

        if direction == "supports":
            support_signals += 1
        else:
            contradiction_signals += 1

    if support_signals > 0 and contradiction_signals > 0:
        return (
            "conflicting",
            support_signals,
            contradiction_signals
        )

    if support_signals > 0:
        return (
            "supports",
            support_signals,
            contradiction_signals
        )

    if contradiction_signals > 0:
        return (
            "contradicts",
            support_signals,
            contradiction_signals
        )

    return (
        "none",
        support_signals,
        contradiction_signals
    )


# ============================================================
# EXPLAINABLE AI
# ============================================================

def explain_prediction(
    processed_text,
    vectorized_text,
    prediction_probability
):

    try:

        feature_names = (
            vectorizer.get_feature_names_out()
        )

        importances = (
            model.feature_importances_
        )

        row = (
            vectorized_text
            .toarray()[0]
        )

        active_features = []

        for index, value in enumerate(row):

            if value > 0:

                active_features.append(
                    (
                        feature_names[index],
                        value,
                        importances[index]
                    )
                )

        active_features.sort(
            key=lambda x:
                x[2] * x[1],
            reverse=True
        )

        return active_features[:8]

    except Exception:

        return []


# ============================================================
# INPUT
# ============================================================

st.html("""
<div class="section-card">

<div class="eyebrow">SECURE ANALYSIS WORKSPACE</div>
<h2>🔍 Analyze News Claim</h2>

<p>
Enter a news statement or article to detect potential
misinformation and independently verify it using
fact-checking and authoritative external evidence.
</p>

</div>
""")


news_text = st.text_area(
    "News statement or article",
    height=220,
    placeholder=(
        "Paste a headline, claim, or short article here..."
    )
)

st.html("""
<div class="section-card" style="padding: 18px 22px;">
<div class="result-label">VERIFICATION PIPELINE</div>
<p class="muted" style="margin: 10px 0 0;">
🌐 Language Detection &nbsp;→&nbsp; 🔄 Translation &nbsp;→&nbsp; 🧹 Preprocessing
&nbsp;→&nbsp; 📊 TF-IDF &nbsp;→&nbsp; 🌲 Random Forest &nbsp;→&nbsp; 🔎 Explainable AI
&nbsp;→&nbsp; 🔍 Fact Check &nbsp;→&nbsp; 🌐 Evidence &nbsp;→&nbsp; 🛡️ Final Verification
</p>
</div>
""")


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🔍 Analyze News",
    type="primary",
    use_container_width=True
):

    if not news_text.strip():

        st.warning(
            "⚠️ Please enter a news statement or article."
        )

        st.stop()

    # ========================================================
    # 1. LANGUAGE DETECTION
    # ========================================================

    st.html("""
    <div class="stage">
    🌐 <b>1. Language Detection</b>
    </div>
    """)

    detected_language = detect_language(
        news_text
    )

    language_name = LANGUAGE_NAMES.get(
        detected_language,
        detected_language
    )

    st.write(
        f"Detected Language: **{language_name}**"
    )

    # ========================================================
    # 2. TRANSLATION
    # ========================================================

    st.html("""
    <div class="stage">
    🔄 <b>2. Translation</b>
    </div>
    """)

    if detected_language == "en":

        english_text = news_text

        st.info(
            "Input is already in English. "
            "Translation is not required."
        )

    else:

        try:

            english_text = translate_to_english(
                news_text,
                detected_language
            )

            st.write(
                "**English Translation:**"
            )

            st.write(
                english_text
            )

        except Exception:

            st.warning(
                "Translation failed. "
                "The original input will be used."
            )

            english_text = news_text

    # ========================================================
    # 3. REPRESENTATIVE CLAIM
    # ========================================================

    st.html("""
    <div class="stage">
    📝 <b>3. News Line Selection</b>
    </div>
    """)

    representative_claim = (
        select_representative_line(
            english_text
        )
    )

    st.write(
        "**Representative Statement:**"
    )

    st.write(
        representative_claim
    )

    # ========================================================
    # 4. PREPROCESSING
    # ========================================================

    st.html("""
    <div class="stage">
    🧹 <b>4. Text Preprocessing</b>
    </div>
    """)

    processed_text = preprocess_text(
        representative_claim
    )

    st.write(
        "Text preprocessing completed successfully."
    )

    # ========================================================
    # 5. TF-IDF
    # ========================================================

    st.html("""
    <div class="stage">
    📊 <b>5. TF-IDF Feature Extraction</b>
    </div>
    """)

    try:

        vectorized_text = vectorizer.transform(
            [processed_text]
        )

        st.write(
            f"**{vectorized_text.shape[1]:,}** "
            "TF-IDF features available to the model."
        )

    except Exception as e:

        st.error(
            "❌ TF-IDF processing failed."
        )

        st.code(
            str(e)
        )

        st.stop()

    # ========================================================
    # 6. RANDOM FOREST
    # ========================================================

    st.html("""
    <div class="stage">
    🌲 <b>6. Random Forest Prediction</b>
    </div>
    """)

    try:

        prediction = model.predict(
            vectorized_text
        )[0]

        probabilities = model.predict_proba(
            vectorized_text
        )[0]

        fake_probability = probabilities[0]

        real_probability = probabilities[1]

    except Exception as e:

        st.error(
            "❌ Model prediction failed."
        )

        st.code(
            str(e)
        )

        st.stop()

    if prediction == 0:

        ml_label = "FAKE NEWS"

        ml_confidence = (
            fake_probability * 100
        )

    else:

        ml_label = "REAL NEWS"

        ml_confidence = (
            real_probability * 100
        )

    # ========================================================
    # 7. MODEL PROBABILITY
    # ========================================================

    st.html("""
    <div class="stage">
    📈 <b>7. Model Probability</b>
    </div>
    """)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Fake Probability",
            f"{fake_probability * 100:.2f}%"
        )

    with col2:

        st.metric(
            "Real Probability",
            f"{real_probability * 100:.2f}%"
        )

    # ========================================================
    # 8. EXPLAINABLE AI
    # ========================================================

    st.html("""
    <div class="stage">
    🔎 <b>8. Explainable AI</b>
    </div>
    """)

    top_features = explain_prediction(
        processed_text,
        vectorized_text,
        ml_confidence
    )

    if top_features:

        feature_rows = "".join(
            f"<tr><td>{html.escape(str(feature))}</td>"
            f"<td>{tfidf_value:.6f}</td>"
            f"<td>{tfidf_value * importance:.6f}</td></tr>"
            for feature, tfidf_value, importance in top_features
        )

        st.html(
            f"""
            <div class="section-card" style="padding: 22px;">
            <p class="muted">These features contributed most strongly to the model's prediction.</p>
            <table style="width:100%; border-collapse:collapse;">
            <thead><tr><th style="text-align:left;">FEATURE</th><th style="text-align:left;">TF-IDF</th><th style="text-align:left;">CONTRIBUTION</th></tr></thead>
            <tbody>{feature_rows}</tbody>
            </table>
            </div>
            """
        )

    else:

        st.info(
            "Feature-level explanation unavailable "
            "for this prediction."
        )

    # ========================================================
    # 9. GOOGLE FACT CHECK
    # ========================================================

    st.html("""
    <div class="stage">
    🔍 <b>9. Google Fact Check</b>
    </div>
    """)

    fact_checks = search_fact_check(
        representative_claim
    )

    if fact_checks:

        st.success(
            f"Found {len(fact_checks)} "
            "relevant fact-check review(s)."
        )

        for index, review in enumerate(
            fact_checks[:5],
            start=1
        ):

            st.html(
                f"""
                <div class="evidence-card">

                <h4>
                🔎 Fact Check {index}
                </h4>

                <b>Publisher:</b>
                {html.escape(
                    str(review["publisher"])
                )}

                <br><br>

                <b>Rating:</b>
                {html.escape(
                    str(review["rating"])
                )}

                </div>
                """
            )

            if review.get("url"):

                st.markdown(
                    f"[🔗 View fact-check review]"
                    f"({review['url']})"
                )

    else:

        st.info(
            "No matching fact-check review found."
        )

    # ========================================================
    # 10. EXTERNAL EVIDENCE
    # ========================================================

    st.html("""
    <div class="stage">
    🌐 <b>10. Authoritative External Evidence</b>
    </div>
    """)

    evidence_results = search_google_news(
        representative_claim
    )

    official_results = [
        r
        for r in evidence_results
        if r.get("tier") == 1
    ]

    established_results = [
        r
        for r in evidence_results
        if r.get("tier") == 2
    ]

    other_results = [
        r
        for r in evidence_results
        if r.get("tier") == 3
    ]

    if evidence_results:

        st.html(
            f"<div class='section-card' style='padding:18px 22px;'>"
            f"<b>{len(evidence_results)} evidence sources</b> found · "
            f"{len(official_results)} official · {len(established_results)} established"
            f"</div>"
        )

        direction_groups = [
            ("supports", "🟢 Supporting Evidence", "direction-supports"),
            ("contradicts", "🔴 Contradicting Evidence", "direction-contradicts"),
            ("unclear", "🟡 Unclear Evidence", "direction-unclear")
        ]

        for group_key, group_title, card_class in direction_groups:
            grouped_results = [
                result for result in evidence_results[:8]
                if result.get("direction", "unclear") == group_key
            ]

            if not grouped_results:
                continue

            st.html(f"<h3>{group_title} <span class='muted'>({len(grouped_results)})</span></h3>")

            for result in grouped_results:
                tier = result.get("tier", 3)
                authority = (
                    "Official Government / Institutional Source"
                    if tier == 1 else
                    "Established News Source"
                    if tier == 2 else
                    "Other Source"
                )
                direction = result.get("direction", "unclear").upper()
                direction_icon = {"SUPPORTS": "🟢", "CONTRADICTS": "🔴", "UNCLEAR": "🟡"}.get(direction, "🟡")
                publisher = html.escape(str(result.get("publisher", "Unknown")))
                domain = html.escape(str(result.get("domain", "Unknown")))
                title = html.escape(str(result.get("title", "")))
                relevance = result.get("relevance", 0) * 100
                overlap = result.get("specific_overlap", 0)
                source_link = html.escape(str(result.get("link", "")), quote=True)

                st.html(
                    f"""
                    <div class="evidence-card {card_class}">
                    <div class="result-label">{publisher} · {domain}</div>
                    <h4 style="margin:8px 0;">{title}</h4>
                    <p class="muted" style="margin:0 0 12px;">{authority}</p>
                    <span class="badge">{direction_icon} {direction}</span>
                    <span class="badge">Relevance {relevance:.1f}%</span>
                    <span class="badge">Claim overlap {overlap} terms</span>
                    {f'<p style="margin:14px 0 0;"><a href="{source_link}" target="_blank">Open Source ↗</a></p>' if source_link else ''}
                    </div>
                    """
                )

    else:

        st.info(
            "No sufficiently relevant external evidence found."
        )

    # ========================================================
    # EVIDENCE ASSESSMENT
    # ========================================================

    (
        evidence_status,
        support_signals,
        contradiction_signals
    ) = assess_authoritative_evidence(
        evidence_results
    )

    st.html(
        f"""
        <div class="section-card" style="padding:20px;">
        <div class="result-label">ANALYSIS SUMMARY</div>
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-top:14px;">
        <div class="evidence-card"><div class="result-label">🌐 LANGUAGE</div><h3>{html.escape(language_name)}</h3></div>
        <div class="evidence-card"><div class="result-label">🌲 ML PREDICTION</div><h3>{html.escape(ml_label)}</h3></div>
        <div class="evidence-card"><div class="result-label">📊 ML CONFIDENCE</div><h3>{ml_confidence:.1f}%</h3></div>
        <div class="evidence-card"><div class="result-label">🌐 EVIDENCE SOURCES</div><h3>{len(evidence_results)}</h3></div>
        </div>
        </div>
        """
    )

    # ========================================================
    # 11. FINAL RESULT
    # ========================================================

    st.html("""
    <div class="stage">
    🛡️ <b>11. Final Result</b>
    </div>
    """)

    # --------------------------------------------------------
    # ML RESULT CARD
    # --------------------------------------------------------

    if ml_label == "REAL NEWS":

        result_icon = "🟢"

    else:

        result_icon = "🔴"

    result_class = "result-real" if ml_label == "REAL NEWS" else ""
    st.html(
        f"""
        <div class="final-card {result_class}">
        <div class="result-label">FINAL MODEL RESULT</div>
        <h2 style="margin:10px 0 4px;">{result_icon} {html.escape(ml_label)}</h2>
        <p class="muted">Random Forest model confidence: <b>{ml_confidence:.2f}%</b></p>
        <div style="display:flex; justify-content:space-between; font-size:.86rem; margin:18px 0 7px;"><span>Fake {fake_probability * 100:.2f}%</span><span>Real {real_probability * 100:.2f}%</span></div>
        <div class="probability-track"><div class="probability-fill" style="width:{ml_confidence:.2f}%;"></div></div>
        </div>
        """
    )

        # ========================================================
    # FINAL EVIDENCE LOGIC
    # ========================================================

    # --------------------------------------------------------
    # FINAL EVIDENCE STRENGTH
    # --------------------------------------------------------

    official_support_signals = sum(
        1
        for result in evidence_results
        if (
            result.get("tier") == 1
            and result.get("direction") == "supports"
            and (
                (
                    result.get("relevance", 0) >= 0.25
                    and result.get("specific_overlap", 0) >= 2
                )
                or result.get("specific_overlap", 0) >= 3
            )
        )
    )

    official_contradiction_signals = sum(
        1
        for result in evidence_results
        if (
            result.get("tier") == 1
            and result.get("direction") == "contradicts"
            and (
                (
                    result.get("relevance", 0) >= 0.25
                    and result.get("specific_overlap", 0) >= 2
                )
                or result.get("specific_overlap", 0) >= 3
            )
        )
    )

    strong_tier2_supports = [
        result
        for result in evidence_results
        if (
            result.get("tier") == 2
            and result.get("direction") == "supports"
            and (
                (
                    result.get("relevance", 0) >= 0.30
                    and result.get("specific_overlap", 0) >= 3
                )
                or (
                    result.get("relevance", 0) >= 0.40
                    and result.get("specific_overlap", 0) >= 2
                )
            )
        )
    ]

    strong_tier2_contradictions = [
        result
        for result in evidence_results
        if (
            result.get("tier") == 2
            and result.get("direction") == "contradicts"
            and (
                (
                    result.get("relevance", 0) >= 0.30
                    and result.get("specific_overlap", 0) >= 3
                )
                or (
                    result.get("relevance", 0) >= 0.40
                    and result.get("specific_overlap", 0) >= 2
                )
            )
        )
    ]

    exceptional_tier2_support = any(
        result.get("relevance", 0) >= 0.55
        and result.get("specific_overlap", 0) >= 5
        for result in strong_tier2_supports
    )

    exceptional_tier2_contradiction = any(
        result.get("relevance", 0) >= 0.55
        and result.get("specific_overlap", 0) >= 5
        for result in strong_tier2_contradictions
    )

    strong_support = (
        evidence_status == "supports"
        and (
            official_support_signals >= 1
            or len(strong_tier2_supports) >= 2
            or exceptional_tier2_support
            or any(
                result.get("relevance", 0) >= 0.40
                and result.get("specific_overlap", 0) >= 5
                for result in strong_tier2_supports
            )
        )
    )

    strong_contradiction = (
        evidence_status == "contradicts"
        and (
            official_contradiction_signals >= 1
            or len(strong_tier2_contradictions) >= 2
            or exceptional_tier2_contradiction
            or any(
                result.get("relevance", 0) >= 0.40
                and result.get("specific_overlap", 0) >= 5
                for result in strong_tier2_contradictions
            )
        )
    )

    # --------------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------------

    final_label = ml_label
    evidence_overrode_ml = False

    if strong_support:

        final_label = "REAL NEWS"

        if ml_label != final_label:
            evidence_overrode_ml = True

    elif strong_contradiction:

        final_label = "FAKE NEWS"

        if ml_label != final_label:
            evidence_overrode_ml = True

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    if final_label == "REAL NEWS":

        final_icon = "🟢"

    else:

        final_icon = "🔴"

    if strong_support:

        final_message = (
            "Strong authoritative evidence supports the claim."
        )

    elif strong_contradiction:

        final_message = (
            "Strong authoritative evidence contradicts the claim."
        )

    elif evidence_status == "supports":

        final_message = (
            "Relevant supporting evidence was found, "
            "but it is not strong enough to override "
            "the Random Forest result."
        )

    elif evidence_status == "contradicts":

        final_message = (
            "Relevant contradicting evidence was found, "
            "but it is not strong enough to override "
            "the Random Forest result."
        )

    elif evidence_status == "conflicting":

        final_message = (
            "Authoritative sources contain conflicting evidence. "
            "The Random Forest result is retained."
        )

    else:

        final_message = (
            "No sufficiently strong authoritative evidence "
            "was found to override the Random Forest result."
        )

    st.html(
        f"""
        <div class="section-card"
             style="padding:22px; margin-top:20px;">

        <div class="result-label">
        🛡️ EVIDENCE-VERIFIED FINAL RESULT
        </div>

        <h2 style="margin:10px 0 6px;">
        {final_icon} {html.escape(final_label)}
        </h2>

        <p class="muted">
        {html.escape(final_message)}
        </p>

        </div>
        """
    )

    # --------------------------------------------------------
    # SUPPORTING EVIDENCE
    # --------------------------------------------------------

    if evidence_status == "supports":

        if strong_support:

            st.success(
                "🟢 Strong authoritative evidence "
                "supports the news claim."
            )

        else:

            st.info(
                "🟢 Relevant supporting evidence was found, "
                "but it is not strong enough to override "
                "the Random Forest result."
            )

        st.write(
            f"**Evidence Support Signals:** "
            f"{support_signals}"
        )

        st.write(
            f"**Evidence Contradiction Signals:** "
            f"{contradiction_signals}"
        )

        if evidence_overrode_ml:

            st.warning(
                "⚠️ ML–Evidence Conflict Resolved"
            )

            st.info(
                f"The Random Forest predicted "
                f"**{ml_label}**, but strong authoritative "
                f"evidence supports the claim. "
                f"The final result is therefore "
                f"**{final_label}**."
            )

        elif strong_support:

            st.success(
                "✅ The Random Forest prediction and "
                "strong authoritative evidence agree."
            )

    # --------------------------------------------------------
    # CONTRADICTING EVIDENCE
    # --------------------------------------------------------

    elif evidence_status == "contradicts":

        if strong_contradiction:

            st.error(
                "🔴 Strong authoritative evidence "
                "contradicts the news claim."
            )

        else:

            st.warning(
                "🔴 Relevant contradicting evidence was found, "
                "but it is not strong enough to override "
                "the Random Forest result."
            )

        st.write(
            f"**Evidence Support Signals:** "
            f"{support_signals}"
        )

        st.write(
            f"**Evidence Contradiction Signals:** "
            f"{contradiction_signals}"
        )

        if evidence_overrode_ml:

            st.warning(
                "⚠️ ML–Evidence Conflict Resolved"
            )

            st.info(
                f"The Random Forest predicted "
                f"**{ml_label}**, but strong authoritative "
                f"evidence contradicts the claim. "
                f"The final result is therefore "
                f"**{final_label}**."
            )

        elif strong_contradiction:

            st.error(
                "The Random Forest prediction and "
                "strong authoritative evidence agree."
            )

    # --------------------------------------------------------
    # CONFLICTING EVIDENCE
    # --------------------------------------------------------

    elif evidence_status == "conflicting":

        st.warning(
            "🟠 Conflicting authoritative evidence detected."
        )

        st.write(
            f"**Supporting Signals:** "
            f"{support_signals}"
        )

        st.write(
            f"**Contradicting Signals:** "
            f"{contradiction_signals}"
        )

        st.info(
            "Authoritative sources disagree. "
            f"The final result remains the Random Forest "
            f"prediction: **{ml_label}**."
        )

    # --------------------------------------------------------
    # NO STRONG AUTHORITATIVE EVIDENCE
    # --------------------------------------------------------

    else:

        if established_results:

            st.warning(
                "🔵 Relevant established-news evidence found, "
                "but it is not strong enough to override "
                "the Random Forest result."
            )

            st.write(
                f"**Established-news evidence:** "
                f"{len(established_results)}"
            )

        else:

            st.info(
                "🟡 No sufficiently strong authoritative "
                "evidence was found."
            )

        st.write(
            f"The final result remains the Random Forest "
            f"prediction: **{ml_label}**."
        )

    # ========================================================
    # TRANSPARENCY
    # ========================================================

    with st.expander("🔬 System Transparency", expanded=False):
        st.html("""
    <div style="padding: 8px 4px 4px;">

    <p>
    <b>NEWS SHIELD AI uses independent verification layers:</b>
    </p>

    <ol>
        <li>🌐 Language Detection</li>
        <li>🔄 Translation</li>
        <li>🧹 Text Preprocessing</li>
        <li>📊 TF-IDF Feature Extraction</li>
        <li>🌲 Random Forest Classification</li>
        <li>📈 Model Probability</li>
        <li>🔎 Explainable AI</li>
        <li>🔍 Google Fact Check Search</li>
        <li>🌐 External Evidence Search</li>
        <li>🔬 Evidence Direction Analysis</li>
        <li>🛡️ Final Combined Analysis</li>
    </ol>

    <p>
    <b>Important:</b>
    ML confidence does not automatically mean that a claim
    is objectively true or false.
    </p>

    <p>
    External evidence is presented independently and does not
    silently overwrite the trained machine-learning model.
    </p>

    </div>
        """)

    # ========================================================
    # FOOTER
    # ========================================================

    st.html("""
    <div class="footer-card">

    🛡️ <b>NEWS SHIELD AI</b>

    <br>

    Multilingual Fake News Detection with
    Explainable AI and Evidence Verification

    </div>
    """)