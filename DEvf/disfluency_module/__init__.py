# disfluency_module/__init__.py

from .core.pipeline import run


def process(text: str, config: dict | None = None) -> dict:
    """
    Full processing for final transcripts.

    Args:
        text: input text.
        config: currently ignored (kept for future extension).
    """
    return run(text)


def process_partial(text: str, config: dict | None = None) -> str:
    """
    Lightweight helper for streaming chunks.
    Returns only cleaned text.

    Args:
        text: input text.
        config: currently ignored (kept for future extension).
    """
    return run(text)["cleaned_text"]
