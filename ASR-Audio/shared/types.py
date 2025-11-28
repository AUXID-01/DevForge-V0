from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import time

@dataclass
class TranscriptChunk:  # YOUR OUTPUT FORMAT
    """What you hand off to other teams"""
    raw_text: str
    speaker_turn: int = 0
    confidence: float = 0.0
    duration_ms: float = 0.0
    language: str = "en"
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}
