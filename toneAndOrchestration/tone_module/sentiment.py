# tone_module/sentiment.py
"""
Lightweight sentiment wrapper. Uses vaderSentiment or textblob if available.
If not installed, falls back to a very small heuristic scorer.
"""
from typing import Tuple

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _HAS_VADER = True
except Exception:
    _HAS_VADER = False

try:
    from textblob import TextBlob
    _HAS_TEXTBLOB = True
except Exception:
    _HAS_TEXTBLOB = False

class SentimentAnalyzer:
    def __init__(self):
        if _HAS_VADER:
            self._vader = SentimentIntensityAnalyzer()
        else:
            self._vader = None

    def polarity(self, text: str) -> float:
        """
        Returns polarity score in range [-1, 1] where positive means positive sentiment.
        """
        if not text:
            return 0.0
        if self._vader:
            scores = self._vader.polarity_scores(text)
            return scores["compound"]
        if _HAS_TEXTBLOB:
            tb = TextBlob(text)
            return tb.sentiment.polarity
        # Fallback heuristic: count exclamation and presence of positive/negative keywords
        low = text.lower()
        score = 0.0
        positives = ["good", "great", "excellent", "awesome", "love", "happy", "thanks"]
        negatives = ["bad", "terrible", "hate", "problem", "sad", "angry"]
        for p in positives:
            if p in low:
                score += 0.2
        for n in negatives:
            if n in low:
                score -= 0.2
        score += low.count("!") * 0.05
        # clamp
        return max(-1.0, min(1.0, score))

    def subjectivity(self, text: str) -> float:
        if _HAS_TEXTBLOB:
            tb = TextBlob(text)
            return tb.sentiment.subjectivity
        # fallback: heuristic
        return 0.5
