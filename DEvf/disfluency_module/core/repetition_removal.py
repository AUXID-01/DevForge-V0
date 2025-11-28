# disfluency_module/core/repetition_removal.py

from typing import List
from collections import deque

from .preprocessing import normalize_text, tokenize, detokenize
from ..config import WINDOWED_BIGRAM_WINDOW


def _remove_consecutive_token_dups(tokens: List[str]) -> List[str]:
    """
    Stage 1: remove consecutive duplicate tokens (case-insensitive).

    Example:
      "I I want want to to go" -> "I want to go"
    """
    if not tokens:
        return tokens

    cleaned = [tokens[0]]
    for token in tokens[1:]:
        if token.lower() != cleaned[-1].lower():
            cleaned.append(token)
    return cleaned


def _remove_immediate_bigram_repeats(tokens: List[str]) -> List[str]:
    """
    Stage 2: remove immediate repeated bigrams:

      "I want I want to thank you" -> "I want to thank you"
      "we should we should go"     -> "we should go"
    """
    cleaned: List[str] = []
    i = 0
    while i < len(tokens):
        if i + 3 < len(tokens):
            a1, b1, a2, b2 = tokens[i:i + 4]
            if a1.lower() == a2.lower() and b1.lower() == b2.lower():
                cleaned.extend([a1, b1])
                i += 4
                continue
        cleaned.append(tokens[i])
        i += 1
    return cleaned


def _remove_windowed_bigram_repeats(tokens: List[str], window_size: int) -> List[str]:
    """
    Stage 3: remove repeated bigrams within a sliding window.

    Catches patterns like:
      "I could I should I could I should try harder"
    -> "I could I should try harder"
    """
    if len(tokens) < 2:
        return tokens

    cleaned: List[str] = []
    recent_bigrams = deque(maxlen=window_size)  # (w1_lower, w2_lower)

    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens):
            w1 = tokens[i]
            w2 = tokens[i + 1]
            bigram_key = (w1.lower(), w2.lower())

            if bigram_key in recent_bigrams:
                # Skip this repeated bigram
                i += 2
                continue

            # Keep and remember
            cleaned.extend([w1, w2])
            recent_bigrams.append(bigram_key)
            i += 2
        else:
            # Last single token
            cleaned.append(tokens[i])
            i += 1

    return cleaned


def _collapse_could_should(tokens: List[str]) -> List[str]:
    """
    Stage 4: polish for written English.

    If sentence starts with:
      "I could I should ..."
    collapse to:
      "I should ..."

    Example:
      "I could I should try harder" -> "I should try harder"
    """
    if len(tokens) < 4:
        return tokens

    if (
        tokens[0].lower() == "i"
        and tokens[1].lower() == "could"
        and tokens[2].lower() == "i"
        and tokens[3].lower() == "should"
    ):
        # Drop "I could", keep from "I should" onward
        return tokens[2:]

    return tokens


def _remove_phrase_repetitions(tokens: List[str]) -> List[str]:
    """
    Stage 5: Remove longer phrase repetitions (3+ words).
    
    Example:
      "I think we should I think we should go" -> "I think we should go"
    """
    if len(tokens) < 6:
        return tokens
    
    cleaned = []
    i = 0
    while i < len(tokens):
        # Check for 3-word phrase repetition
        if i + 5 < len(tokens):
            phrase1 = tokens[i:i+3]
            phrase2 = tokens[i+3:i+6]
            
            # Check if phrases match (case-insensitive)
            if (phrase1[0].lower() == phrase2[0].lower() and
                phrase1[1].lower() == phrase2[1].lower() and
                phrase1[2].lower() == phrase2[2].lower()):
                # Skip the repetition, keep only first occurrence
                cleaned.extend(phrase1)
                i += 6
                continue
        
        cleaned.append(tokens[i])
        i += 1
    
    return cleaned


def remove_repetitions_advanced(text: str) -> str:
    """
    Enhanced low-latency repetition pipeline:

      1) Remove consecutive duplicate tokens (I I -> I).
      2) Remove immediate repeated bigrams (A B A B -> A B).
      3) Remove windowed repeated bigrams within a small window.
      4) Collapse "I could I should" to "I should".
      5) Remove longer phrase repetitions (3+ words).
    """
    tokens = tokenize(text)
    if not tokens:
        return text

    tokens = _remove_consecutive_token_dups(tokens)
    tokens = _remove_immediate_bigram_repeats(tokens)
    tokens = _remove_windowed_bigram_repeats(tokens, WINDOWED_BIGRAM_WINDOW)
    tokens = _collapse_could_should(tokens)
    tokens = _remove_phrase_repetitions(tokens)

    result = detokenize(tokens)
    return normalize_text(result)
