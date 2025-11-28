# tone_module/utils.py
import re
from typing import Dict


_contraction_expansions: Dict[str, str] = {
    "don't": "do not",
    "can't": "cannot",
    "i'm": "I am",
    "it's": "It is",
    "we're": "we are",
    "i'll": "I will",
    "you're": "you are",
    "they're": "they are",
    "that's": "that is",
    "there's": "there is",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "doesn't": "does not",
    "didn't": "did not",
    "won't": "will not",
    "wouldn't": "would not",
}

_whitespace_re = re.compile(r"\s+")
_punct_re = re.compile(r"([^\w\s'])")  # capture punctuation (leave apostrophes)

def normalize_whitespace(text: str) -> str:
    return _whitespace_re.sub(" ", text).strip()

def expand_contractions(text: str) -> str:
    # Lowercase matching but try to preserve capitalization later.
    def replace(match):
        k = match.group(0).lower()
        return _contraction_expansions.get(k, k)
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in _contraction_expansions.keys()) + r")\b", flags=re.IGNORECASE)
    return pattern.sub(replace, text)

def apply_mapping(text: str, mapping: Dict[str, str]) -> str:
    """
    Apply simple token/phrase mapping. Lowercase-aware but preserves case of first char if needed.
    """
    if not mapping:
        return text
    # Replace longer keys first to avoid partial matches
    keys = sorted(mapping.keys(), key=lambda x: -len(x))
    def repl(m):
        k = m.group(0)
        # find mapping by lowercase
        mapped = mapping.get(k, mapping.get(k.lower()))
        if mapped is None:
            return k
        # preserve capitalization of first letter
        if k and k[0].isupper():
            return mapped[0].upper() + mapped[1:]
        return mapped
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in keys) + r")\b", flags=re.IGNORECASE)
    return pattern.sub(repl, text)

def simple_sentence_split_and_capitalize(text: str) -> str:
    """
    Naive sentence splitter / capitalizer: splits on punctuation, ensures each sentence starts capitalized.
    Lightweight and fast for streaming usage.
    """
    text = text.strip()
    if not text:
        return text
    # Ensure punctuation at sentence ends: if long chunk with no punctuation, add a '.' 
    if len(text) > 40 and not re.search(r"[.!?]\s*$", text):
        text = text + "."
    # Split on sentence terminators, preserve terminator
    parts = re.split(r'([.!?]\s+)', text)
    out = []
    for i in range(0, len(parts), 2):
        sent = parts[i]
        term = parts[i+1] if i+1 < len(parts) else ""
        sent = sent.strip()
        if not sent:
            continue
        # Capitalize first letter if alphabetic
        if sent:
            sent = sent[0].upper() + sent[1:]
        out.append(sent + term.strip())
    return " ".join(out)

def remove_words(text: str, words):
    """
    Remove standalone words/phrases listed in words.
    """
    if not words:
        return text
    keys = sorted(words, key=lambda x: -len(x))
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in keys) + r")\b", flags=re.IGNORECASE)
    return pattern.sub("", text)

def reduce_intensifiers(text: str, intensifiers):
    if not intensifiers:
        return text
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in intensifiers) + r")\b\s*", flags=re.IGNORECASE)
    return pattern.sub("", text)

def safe_strip_punctuation(text: str) -> str:
    # collapse multiple punctuation, trim leading/trailing punctuation
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[.]{2,}", ".", text)
    text = text.strip()
    return text
