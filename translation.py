
from IndicTransToolkit import IndicProcessor
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re


# ============================================================
# INDIC TRANS2 CONFIGURATION
# ============================================================

MODEL_NAME = "ai4bharat/indictrans2-indic-en-dist-200M"

TARGET_LANGUAGE = "eng_Latn"


# ============================================================
# LANGUAGE CODE MAPPING
# ============================================================

INDIC_LANGUAGE_CODES = {
    "ta": "tam_Taml",       # Tamil
    "hi": "hin_Deva",       # Hindi
    "te": "tel_Telu",       # Telugu
    "kn": "kan_Knda",       # Kannada
    "ml": "mal_Mlym",       # Malayalam
    "bn": "ben_Beng",       # Bengali
    "mr": "mar_Deva",       # Marathi
}


# ============================================================
# LOAD INDIC TRANS2
# ============================================================

print("Loading IndicTrans2...")

processor = IndicProcessor(
    inference=True
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("IndicTrans2 loaded successfully!")


# ============================================================
# TRANSLATION OUTPUT CLEANING
# ============================================================

def clean_translation_output(text):
    """
    Cleans accidental Unicode artifacts from IndicTrans2
    English translation output.
    """

    if not isinstance(text, str):
        return text

    # --------------------------------------------------------
    # Fix escaped Unicode patterns
    # Example:
    # Authorities\ u093C
    # becomes:
    # Authorities\u093C
    # --------------------------------------------------------

    text = re.sub(
        r"\\\s+u([0-9a-fA-F]{4})",
        r"\\u\1",
        text
    )

    # --------------------------------------------------------
    # Decode valid Unicode escape sequences
    # --------------------------------------------------------

    def decode_unicode_match(match):
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)

    text = re.sub(
        r"\\u([0-9a-fA-F]{4})",
        decode_unicode_match,
        text
    )

    # --------------------------------------------------------
    # Remove accidental standalone Devanagari characters
    # from English translation.
    #
    # Example:
    # Authorities़ has
    #
    # becomes:
    # Authorities has
    #
    # This is specifically useful for accidental Marathi/
    # Hindi Unicode artifacts appearing in English output.
    # --------------------------------------------------------

    text = re.sub(
        r"(?<![\u0900-\u097F])[\u0900-\u097F]",
        "",
        text
    )

    # --------------------------------------------------------
    # Remove accidental control characters
    # --------------------------------------------------------

    text = "".join(
        char
        for char in text
        if char.isprintable() or char in "\n\t"
    )

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# TRANSLATION FUNCTION
# ============================================================

def translate_to_english(text, language_code):

    # --------------------------------------------------------
    # English does not need translation
    # --------------------------------------------------------

    if language_code == "en":
        return text

    # --------------------------------------------------------
    # Get IndicTrans2 language code
    # --------------------------------------------------------

    source_language = INDIC_LANGUAGE_CODES.get(
        language_code
    )

    if source_language is None:
        raise ValueError(
            f"Unsupported language for IndicTrans2: "
            f"{language_code}"
        )

    # --------------------------------------------------------
    # PREPROCESS
    # --------------------------------------------------------

    batch = processor.preprocess_batch(
        [text],
        src_lang=source_language,
        tgt_lang=TARGET_LANGUAGE,
        visualize=False
    )

    # --------------------------------------------------------
    # TOKENIZE
    # --------------------------------------------------------

    inputs = tokenizer(
        batch,
        padding="longest",
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )

    # --------------------------------------------------------
    # TRANSLATE
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            use_cache=True,
            min_length=0,
            max_length=256,
            num_beams=5,
            num_return_sequences=1
        )

    # --------------------------------------------------------
    # DECODE
    # --------------------------------------------------------

    decoded = tokenizer.batch_decode(
        outputs,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )

    # --------------------------------------------------------
    # POSTPROCESS
    # --------------------------------------------------------

    result = processor.postprocess_batch(
        decoded,
        lang=TARGET_LANGUAGE
    )

    translated_text = result[0]

    # --------------------------------------------------------
    # CLEAN TRANSLATED TEXT
    # --------------------------------------------------------

    translated_text = clean_translation_output(
        translated_text
    )
    # ========================================================
    # TARGETED TAMIL DOCKING TERM CORRECTION
    # ========================================================

    if language_code == "ta":

        tamil_docking_terms = [
            "இணைத்தது",
            "இணைத்தனர்",
            "இணைக்கப்பட்டது",
            "இணைந்தது",
            "டாக் செய்தது",
            "டாக்கிங்",
            "டாக்கிங் செய்தது",
            "செயற்கைக்கோள்களை இணைத்தது",
            "செயற்கைக்கோள்கள் இணைந்தன"
        ]

        tamil_space_terms = [
            "விண்வெளி",
            "செயற்கைக்கோள்",
            "செயற்கைக்கோள்கள்",
            "ஸ்பேடெக்ஸ்",
            "SpaDeX",
            "ISRO",
            "இஸ்ரோ"
        ]

        has_docking_term = any(
            term in text
            for term in tamil_docking_terms
        )

        has_space_term = any(
            term in text
            for term in tamil_space_terms
        )

        if has_docking_term and has_space_term:

            translated_text = re.sub(
                r"\blaunched\b",
                "docked",
                translated_text,
                flags=re.IGNORECASE
            )

    return translated_text

