# disfluency_module/core/preprocessing.py

def normalize_text(text: str) -> str:
    """
    Strip leading/trailing spaces and collapse multiple spaces to one.
    """
    text = text.strip()
    return " ".join(text.split())


def tokenize(text: str) -> list:
    """
    Simple whitespace tokenizer.
    """
    return text.split()


def detokenize(tokens: list) -> str:
    """
    Join tokens back into a string.
    """
    return " ".join(tokens)
