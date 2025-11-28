# orchestrator/tests/test_full_mock_pipeline.py

import time

from mocks.mock_asr import mock_asr_stream
from mocks.mock_cleaner import mock_cleaner_stage
from mocks.mock_grammar import mock_grammar_stage

from orchestrator.orchestrator import PipelineOrchestrator
from schemas.pipeline_message import PipelineMessage
from orchestrator import latency_logger


def test_full_mock_pipeline_formal_mode(monkeypatch):
    """
    End-to-end through mocks:
      mock_asr -> mock_cleaner -> mock_grammar -> PipelineOrchestrator

    Checks:
      - ASR fillers and repetitions are removed by cleaner
      - Grammar adds basic punctuation/capitalization
      - Orchestrator buffers chunks and emits END_TONE
      - Final text is non-empty, formal-ish, and latency logged
    """

    utt_id = "utt_full_1"

    # 1) ASR stage (mock)
    asr_msgs = mock_asr_stream(utt_id)

    # set a consistent end_of_speech_time on END_ASR
    eos_time = time.time() - 0.4  # 400 ms ago
    for m in asr_msgs:
        if m.event == "END_ASR":
            m.end_of_speech_time = eos_time

    # 2) Cleaner stage
    clean_msgs = mock_cleaner_stage(asr_msgs)

    # 3) Grammar stage
    grammar_msgs = mock_grammar_stage(clean_msgs)

    # 4) Tone & orchestration
    orch = PipelineOrchestrator(tone_mode="formal")

    logged = {}

    def fake_log(stage: str, latency_ms: int):
        logged["stage"] = stage
        logged["latency"] = latency_ms

    monkeypatch.setattr(latency_logger.LatencyLogger, "log", staticmethod(fake_log))

    final_msg: PipelineMessage | None = None

    for gm in grammar_msgs:
        out = orch.process_message(gm)
        # we only care about final END_TONE at the end
        if out is not None and out.event == "END_TONE":
            final_msg = out

    # Assertions on final output
    assert final_msg is not None
    assert final_msg.event == "END_TONE"
    assert final_msg.is_final is True
    assert final_msg.id == utt_id
    assert len(final_msg.text.strip()) > 0
    assert final_msg.text.strip().endswith(".")

    # Check that fillers and obvious repetitions are gone
    low = final_msg.text.lower()
    assert "um" not in low
    assert "you know" not in low
    assert " i i " not in low

    # Formal-ish hints (not strict, but expected direction)
    assert "thank" in low  # from "thank you for coming..."
    # latency logged
    assert logged["stage"] == "Final Tone Stage"
    assert logged["latency"] >= 0
