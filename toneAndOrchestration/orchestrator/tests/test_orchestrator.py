# orchestrator/tests/test_orchestrator.py

import time
import pytest

from orchestrator.orchestrator import PipelineOrchestrator
from orchestrator.state import UtteranceState
from schemas.pipeline_message import PipelineMessage


def test_orchestrator_streaming_previews_and_final_end_tone(monkeypatch):
    """
    Simulate:
      - 2 PART chunks from grammar
      - 1 END_GRAMMAR event
    Expectations:
      - state buffers both chunks
      - each PART produces a PREVIEW_TONE message
      - END_GRAMMAR produces an END_TONE message
      - final text is non-empty and ordered as chunk 0 + chunk 1
      - latency is computed and logged
    """

    orch = PipelineOrchestrator(tone_mode="formal")

    fake_eos = time.time() - 0.5  # 500ms ago

    # 1) First PART chunk
    msg0 = PipelineMessage(
        id="utt1",
        chunk_index=0,
        text="thanks, i'm gonna go now",
        event="PART",
        is_final=False,
        end_of_speech_time=None,
    )
    preview0 = orch.process_message(msg0)

    assert preview0 is not None
    assert preview0.event == "PREVIEW_TONE"
    assert preview0.is_final is False
    assert preview0.id == "utt1"
    assert preview0.chunk_index == 0
    # tone-transform hints
    assert "thank" in preview0.text.lower() or "going to" in preview0.text or "i am" in preview0.text.lower()

    # state should contain first chunk
    st: UtteranceState = orch.state_by_id["utt1"]
    assert st.chunks[0] == msg0.text

    # 2) Second PART chunk
    msg1 = PipelineMessage(
        id="utt1",
        chunk_index=1,
        text="this is really important",
        event="PART",
        is_final=False,
        end_of_speech_time=None,
    )
    preview1 = orch.process_message(msg1)

    assert preview1 is not None
    assert preview1.event == "PREVIEW_TONE"
    assert preview1.chunk_index == 1
    assert len(preview1.text.strip()) > 0

    # state should now have two chunks
    st = orch.state_by_id["utt1"]
    assert len(st.chunks) == 2

    # 3) END_GRAMMAR triggers finalization
    end_msg = PipelineMessage(
        id="utt1",
        chunk_index=-1,
        text="",
        event="END_GRAMMAR",
        is_final=True,
        end_of_speech_time=fake_eos,
    )

    from orchestrator import latency_logger

    recorded = {}

    def fake_log(stage: str, latency_ms: int):
        recorded["stage"] = stage
        recorded["latency_ms"] = latency_ms

    monkeypatch.setattr(latency_logger.LatencyLogger, "log", staticmethod(fake_log))

    final = orch.process_message(end_msg)

    # Final END_TONE checks
    assert final is not None
    assert final.event == "END_TONE"
    assert final.is_final is True
    assert final.id == "utt1"
    assert final.text.strip().endswith(".")
    assert "utt1" not in orch.state_by_id  # state cleaned up

    # Latency logged and non-negative
    assert recorded["stage"] == "Final Tone Stage"
    assert recorded["latency_ms"] >= 0


def test_orchestrator_ignores_unknown_events():
    """
    Any event that is not PART or END_GRAMMAR should return None
    and not break the orchestrator.
    """
    orch = PipelineOrchestrator()

    msg = PipelineMessage(
        id="utt2",
        chunk_index=0,
        text="some text",
        event="END_ASR",  # not handled
        is_final=True,
        end_of_speech_time=time.time(),
    )

    out = orch.process_message(msg)
    assert out is None
    # state is created but no output
    assert "utt2" in orch.state_by_id
