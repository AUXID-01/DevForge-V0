# tone_module/tests/test_sentiment.py
from tone_module.sentiment import SentimentAnalyzer

def test_sentiment_polarity_neutral():
    sa = SentimentAnalyzer()
    assert abs(sa.polarity("")) == 0.0

def test_sentiment_polarity_positive_negative():
    sa = SentimentAnalyzer()
    p = sa.polarity("I love this product, it's great!")
    n = sa.polarity("This was terrible and I hate it.")
    assert p >= 0
    assert n <= 0
