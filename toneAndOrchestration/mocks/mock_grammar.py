# mocks/mock_grammar.py
from typing import List
import re
from schemas.pipeline_message import PipelineMessage


def _basic_punctuate(text: str) -> str:
    """
    Very naive grammar/formatting:
    - ensures first char uppercase
    - adds period at end if missing
    """
    t = text.strip()
    if not t:
        return t
    # capitalize first letter
    t = t[0].upper() + t[1:]
    # add period if missing terminal punctuation
    if not re.search(r"[.!?]$", t):
        t += "."
    return t


def mock_grammar_stage(messages: List[PipelineMessage]) -> List[PipelineMessage]:
    """
    Take cleaned messages and add simple punctuation/capitalization.
    Converts END_CLEAN into END_GRAMMAR.
    """
    out: List[PipelineMessage] = []
    for msg in messages:
        if msg.event == "PART":
            t = _basic_punctuate(msg.text)
            out.append(
                PipelineMessage(
                    id=msg.id,
                    chunk_index=msg.chunk_index,
                    text=t,
                    event="PART",
                    is_final=msg.is_final,
                    end_of_speech_time=msg.end_of_speech_time,
                )
            )
        elif msg.event == "END_CLEAN":
            out.append(
                PipelineMessage(
                    id=msg.id,
                    chunk_index=-1,
                    text="",
                    event="END_GRAMMAR",
                    is_final=True,
                    end_of_speech_time=msg.end_of_speech_time,
                )
            )
    return out
