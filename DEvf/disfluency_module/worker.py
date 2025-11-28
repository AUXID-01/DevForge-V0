# disfluency_module/worker.py

from typing import Any, Dict, List, Optional
from queue import Queue
import sys
from pathlib import Path

from . import process_partial
from .core.preprocessing import tokenize, detokenize
from .config import CONTEXT_SIZE
from .schema import PipelineMessage

# Import rolling window deduplicator
project_root = Path(__file__).parent.parent.parent.parent
unified_pipeline_path = project_root / "unified_pipeline"
if str(unified_pipeline_path) not in sys.path:
    sys.path.insert(0, str(unified_pipeline_path))

try:
    from chunk_deduplicator import RollingWindowDeduplicator
except ImportError:
    # Fallback if import fails
    RollingWindowDeduplicator = None


class DisfluencyWorker:
    """
    Streaming disfluency + repetition worker.

    Input:  PipelineMessage from ASR  (event="PART" or "END_ASR")
    Output: PipelineMessage to Grammar (event="PART" or "END_CLEAN")

    Keeps a small per-id sliding context of tokens to catch
    cross-chunk repetitions without reprocessing full history.
    """

    def __init__(self, input_queue: Any, output_queue: Any):
        self.input_queue = input_queue
        self.output_queue = output_queue
        # id -> last CONTEXT_SIZE tokens (from cleaned combined text)
        self.context_by_id: Dict[str, List[str]] = {}
        # Per-ID rolling window deduplicator
        self.deduplicators: Dict[str, 'RollingWindowDeduplicator'] = {}

    def _get_message(self) -> Optional[PipelineMessage]:
        """
        Retrieve a message from the input queue.
        Supports:
          - queue.Queue[PipelineMessage]
          - list[PipelineMessage]
        """
        if isinstance(self.input_queue, Queue):
            if self.input_queue.empty():
                return None
            return self.input_queue.get()

        # list-like
        if self.input_queue:
            return self.input_queue.pop(0)

        return None

    def _put_message(self, msg: PipelineMessage) -> None:
        """
        Send a message to the output queue.
        Supports:
          - queue.Queue[PipelineMessage]
          - list[PipelineMessage]
        """
        if isinstance(self.output_queue, Queue):
            self.output_queue.put(msg)
        else:
            self.output_queue.append(msg)

    def process_message(self, msg: PipelineMessage) -> None:
        """
        Core logic per message.

        - If event == "END_ASR" or "AUTO_STOP":
            -> emit END_CLEAN, clear context.
        - If event == "PART":
            -> combine context + chunk, clean, slice "new" part, update context, emit PART.
        """
        eid = msg.id

        # 1) Handle END_ASR or AUTO_STOP (end of speech from ASR)
        if msg.event == "END_ASR" or msg.event == "AUTO_STOP":
            end_msg = PipelineMessage(
                id=eid,
                chunk_index=-1,
                text="",
                event="END_CLEAN",
                is_final=True,
                end_of_speech_time=msg.end_of_speech_time,
            )
            # clear context and deduplicator
            self.context_by_id.pop(eid, None)
            if eid in self.deduplicators:
                self.deduplicators[eid].reset()
                self.deduplicators.pop(eid, None)
            self._put_message(end_msg)
            return

        # 2) Normal streaming chunk ("PART")
        raw_chunk = msg.text or ""
        
        # Apply rolling window deduplication FIRST (before other processing)
        if RollingWindowDeduplicator is not None:
            if eid not in self.deduplicators:
                self.deduplicators[eid] = RollingWindowDeduplicator(window_size=60)
            
            deduplicator = self.deduplicators[eid]
            raw_chunk, had_overlap = deduplicator.deduplicate(raw_chunk)
            
            # If chunk was completely removed due to overlap, skip it
            if not raw_chunk or not raw_chunk.strip():
                return

        # Get previous context tokens
        context_tokens = self.context_by_id.get(eid, [])
        context_str = detokenize(context_tokens) if context_tokens else ""

        # Combine context + current chunk so we can catch boundary repetitions
        combined = (context_str + " " + raw_chunk).strip() if context_str else raw_chunk

        # Clean combined text (fillers + repetition patterns)
        cleaned_combined = process_partial(combined)

        # Tokenize cleaned combined
        cleaned_tokens = tokenize(cleaned_combined)

        # Determine "new" part relative to context length
        num_context_tokens = len(context_tokens)
        if len(cleaned_tokens) > num_context_tokens:
            new_tokens = cleaned_tokens[num_context_tokens:]
        else:
            new_tokens = []  # cleaning shortened everything into old context

        cleaned_chunk_text = detokenize(new_tokens)

        # Update sliding context with tail of cleaned combined
        self.context_by_id[eid] = cleaned_tokens[-CONTEXT_SIZE:]

        # If this is final chunk for the utterance, clear context
        if msg.is_final:
            self.context_by_id.pop(eid, None)

        # Build outgoing PART message
        out_msg = PipelineMessage(
            id=eid,
            chunk_index=msg.chunk_index,
            text=cleaned_chunk_text,
            event="PART",
            is_final=msg.is_final,
            end_of_speech_time=msg.end_of_speech_time,  # usually None for PART
        )
        self._put_message(out_msg)

    def run_forever(self):
        """
        Simple loop to keep processing messages until input queue is empty
        or a special END_TONE message is seen.
        """
        while True:
            msg = self._get_message()
            if msg is None:
                break

            # Allow raw dicts for safety
            if isinstance(msg, dict):
                msg = PipelineMessage(**msg)

            # Optional global stop
            if msg.event == "END_TONE":
                break

            self.process_message(msg)
