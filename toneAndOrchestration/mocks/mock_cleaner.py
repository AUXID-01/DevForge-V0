# mocks/mock_cleaner.py
from typing import List
import re
from schemas.pipeline_message import PipelineMessage

FILLERS = ["um", "uh", "you know", "like"]


def _remove_fillers(text: str) -> str:
    pattern = re.compile(r"\b(" + "|".join(re.escape(w) for w in FILLERS) + r")\b", flags=re.IGNORECASE)
    return pattern.sub("", text).replace("  ", " ").strip()


def _fix_simple_repetition(text: str) -> str:
    # collapse "I I" -> "I", "really really" -> "really"
    return re.sub(r"\b(\w+)\s+\1\b", r"\1", text, flags=re.IGNORECASE)


def mock_cleaner_stage(messages: List[PipelineMessage]) -> List[PipelineMessage]:
    """
    Take ASR messages and output cleaned messages (still PART + one END_CLEAN).
    """
    out: List[PipelineMessage] = []
    for msg in messages:
        if msg.event == "PART":
            t = _remove_fillers(msg.text)
            t = _fix_simple_repetition(t)
            out.append(
                PipelineMessage(
                    id=msg.id,
                    chunk_index=msg.chunk_index,
                    text=t.strip(),
                    event="PART",
                    is_final=msg.is_final,
                    end_of_speech_time=msg.end_of_speech_time,
                )
            )
        elif msg.event == "END_ASR":
            # propagate end event as END_CLEAN, copying time if present
            out.append(
                PipelineMessage(
                    id=msg.id,
                    chunk_index=-1,
                    text="",
                    event="END_CLEAN",
                    is_final=True,
                    end_of_speech_time=msg.end_of_speech_time,
                )
            )
    return out
