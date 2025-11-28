# schemas/pipeline_message.py
from typing import Optional
from pydantic import BaseModel


class PipelineMessage(BaseModel):
    """
    Shared message object used across ALL pipeline stages.
    This ensures ASR → Cleaner → Grammar → Tone are plug-and-play compatible.
    """

    id: str                     # utterance/session ID (e.g., "utt_42")
    chunk_index: int            # 0,1,2,... or -1 for END events
    text: str                   # chunk text ("" for END events)
    event: str                  # "PART", "END_ASR", "END_CLEAN", "END_GRAMMAR", "END_TONE"
    is_final: bool = False      # ASR: whether this chunk is stable/final
    end_of_speech_time: Optional[float] = None  # set by ASR on END_ASR
