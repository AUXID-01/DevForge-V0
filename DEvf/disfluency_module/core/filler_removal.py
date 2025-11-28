# disfluency_module/core/filler_removal.py

import re
from pathlib import Path
from .preprocessing import normalize_text
from ..config import ENGLISH_FILLERS_PATH

FILLER_PATTERN = None  # global cache


def _load_fillers(path: Path):
    """
    Read filler words from a file and build a compiled regex pattern.
    """
    fillers = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                fillers.append(re.escape(w))

    # Example: r"\b(um|uh|like|you\ know)\b"
    pattern = r"\b(" + "|".join(fillers) + r")\b"
    return re.compile(pattern, flags=re.IGNORECASE)


def init_filler_pattern():
    """
    Lazily initialize global FILLER_PATTERN.
    """
    global FILLER_PATTERN
    if FILLER_PATTERN is None:
        base = Path(__file__).resolve().parents[1]
        path = base / ENGLISH_FILLERS_PATH
        FILLER_PATTERN = _load_fillers(path)


def remove_fillers(text: str) -> str:
    """
    Enhanced filler removal with better pattern matching.
    """
    init_filler_pattern()
    
    # First pass: remove standard fillers
    cleaned = FILLER_PATTERN.sub(" ", text)
    
    # Second pass: remove common filler phrases (more aggressive)
    filler_phrases = [
        r"\byou\s+know\s+what\s+i\s+mean\b",
        r"\bif\s+that\s+makes\s+sense\b",
        r"\bstuff\s+like\s+that\b",
        r"\band\s+stuff\b",
        r"\band\s+things\b",
        r"\bor\s+whatever\b",
        r"\byou\s+get\s+me\b",
        r"\bi\s+feel\s+like\b",
        r"\bi'm\s+like\b",
    ]
    
    for phrase in filler_phrases:
        cleaned = re.sub(phrase, " ", cleaned, flags=re.IGNORECASE)
    
    # Normalize spaces
    cleaned = normalize_text(cleaned)
    return cleaned
