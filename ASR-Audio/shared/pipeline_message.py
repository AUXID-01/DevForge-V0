from typing import Optional
from pydantic import BaseModel

class PipelineMessage(BaseModel):
    id: str                  # session / utterance id, e.g. "utt_123"
    chunk_index: int         # 0,1,2... for ordering; -1 for control events
    text: str                # content for this chunk ("" for END events)
    event: str               # "PART", "END_ASR", "END_CLEAN", "END_GRAMMAR", "END_TONE"
    is_final: bool = False   # ASR: is this chunk stable/final?
    end_of_speech_time: Optional[float] = None  # set by ASR on END_ASR (ms)
