# tone_module/transformer.py
import re
from typing import Dict
import time

import contractions

from schemas.pipeline_message import PipelineMessage
from interfaces.tone_interface import ToneInterface
from tone_module.tone_rules import (
    FORMAL_EXPANSIONS,
    CASUAL_SIMPLIFICATIONS,
    INTENSIFIERS,
    HEDGES,
)


class ToneTransformer(ToneInterface):
    def __init__(self, mode: str = "neutral"):
        self.mode = (mode or "neutral").lower()
        # For streaming use: id -> {chunk_index: text}
        self.buffers: Dict[str, Dict[int, str]] = {}
        # Optional end_of_speech_time tracking
        self.end_of_speech_time_by_id: Dict[str, float] = {}

    # -----------------------------------------
    # Minimal normalization (no grammar)
    # -----------------------------------------
    def _normalize(self, text: str) -> str:
        return text.strip()

    # -----------------------------------------
    # FINAL CLEANUP: remove double spaces
    # -----------------------------------------
    def _final_cleanup(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # -----------------------------------------
    # MAIN TONE TRANSFORMATION (single string)
    # -----------------------------------------
    def _tone_transform(self, text: str) -> str:
        mode = self.mode
        original_text = text

        text = self._normalize(text)

        # NEUTRAL — NO CHANGES (just cleanup)
        if mode == "neutral":
            return self._final_cleanup(original_text)

        # FORMAL MODE
        if mode == "formal":
            text = original_text
            try:
                text = contractions.fix(text)
            except:
                pass  # If contractions library fails, continue
            
            # Expand contractions and casual phrases
            for k, v in FORMAL_EXPANSIONS.items():
                text = re.sub(rf"\b{re.escape(k)}\b", v, text, flags=re.IGNORECASE)
            
            # Remove intensifiers
            words = text.split()
            filtered = [w for w in words if w.lower() not in INTENSIFIERS]
            text = " ".join(filtered)
            
            # Remove hedging phrases
            for hedge in HEDGES:
                pattern = rf"\b{re.escape(hedge)}\b"
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            
            return self._final_cleanup(text)

        # CASUAL MODE
        if mode == "casual":
            text = original_text
            for k, v in CASUAL_SIMPLIFICATIONS.items():
                text = re.sub(rf"\b{re.escape(k)}\b", v, text, flags=re.IGNORECASE)
            return self._final_cleanup(text)

        # CONCISE MODE
        if mode == "concise":
            text = original_text
            # Remove hedging phrases (more aggressive)
            for h in HEDGES:
                pattern = rf"\b{re.escape(h)}\b"
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            
            # Remove intensifiers
            words = text.split()
            filtered = [w for w in words if w.lower() not in INTENSIFIERS]
            text = " ".join(filtered)
            
            # Remove redundant phrases
            text = re.sub(r"\b(i think|i believe|i guess)\s+", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s+(you know|i mean)\s+", " ", text, flags=re.IGNORECASE)
            
            return self._final_cleanup(text)

        return self._final_cleanup(original_text)

    # -----------------------------------------
    # PUBLIC API 1: process one streaming chunk
    # -----------------------------------------
    def process_chunk(self, message: PipelineMessage) -> PipelineMessage:
        """
        Store chunk text for this utterance and return a non-final
        preview with tone applied only to this chunk.
        """
        uid = message.id
        if uid not in self.buffers:
            self.buffers[uid] = {}
        self.buffers[uid][message.chunk_index] = message.text

        if message.end_of_speech_time:
            self.end_of_speech_time_by_id[uid] = message.end_of_speech_time

        preview_text = self._tone_transform(message.text)

        return PipelineMessage(
            id=uid,
            chunk_index=message.chunk_index,
            text=preview_text,
            event="PART",
            is_final=False,
            end_of_speech_time=message.end_of_speech_time,
        )

    # -----------------------------------------
    # PUBLIC API 2: finalize after END_GRAMMAR
    # -----------------------------------------
    def finalize(self, utterance_id: str) -> PipelineMessage:
        """
        Assemble buffered chunks for this utterance in order,
        apply final tone transform, compute latency if possible,
        and emit an END_TONE message.
        """
        chunks = self.buffers.get(utterance_id, {})
        if chunks:
            ordered = [chunks[i] for i in sorted(chunks.keys())]
            joined = " ".join(ordered)
            final_text = self._tone_transform(joined)
            # ensure final period for full utterance
            if final_text and not re.search(r"[.!?]$", final_text):
                final_text += "."
        else:
            final_text = ""

        eos = self.end_of_speech_time_by_id.get(utterance_id)
        # Optional latency calculation (logged elsewhere if you want)
        if eos is not None:
            now = time.time()
            # assume eos is seconds
            _latency_ms = int((now - eos) * 1000)

        # cleanup
        self.buffers.pop(utterance_id, None)
        self.end_of_speech_time_by_id.pop(utterance_id, None)

        return PipelineMessage(
            id=utterance_id,
            chunk_index=0,
            text=final_text,
            event="END_TONE",
            is_final=True,
            end_of_speech_time=eos,
        )

    # -----------------------------------------
    # PUBLIC API 3: single-call helper
    # -----------------------------------------
    def tone_transform(self, text: str, mode: str | None = None) -> str:
        """
        Convenience non-streaming API for unit tests / CLI:
        temporarily switch mode, transform, then restore.
        """
        prev_mode = self.mode
        if mode:
            self.mode = mode.lower()
        try:
            out = self._tone_transform(text)
        finally:
            self.mode = prev_mode
        return out
