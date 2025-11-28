# disfluency_module/core/pipeline.py

import time
from .filler_removal import remove_fillers
from .repetition_removal import remove_repetitions_advanced


def run(text: str) -> dict:
    """
    Internal pipeline:
      1) Remove fillers.
      2) Remove repetitions (pattern-based, low latency).
      3) Return cleaned text + timing.
    """
    start = time.perf_counter()

    no_fillers = remove_fillers(text)
    cleaned = remove_repetitions_advanced(no_fillers)

    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000.0

    return {
        "cleaned_text": cleaned,
        "removed_fillers": [],
        "removed_repetitions": [],
        "processing_time_ms": round(elapsed_ms, 3),
    }
