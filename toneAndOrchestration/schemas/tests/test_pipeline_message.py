# schemas/tests/test_pipeline_message.py
import pytest
from schemas.pipeline_message import PipelineMessage


def test_pipeline_message_creation():
    msg = PipelineMessage(
        id="utt_1",
        chunk_index=0,
        text="hello world",
        event="PART",
        is_final=False,
        end_of_speech_time=None,
    )
    assert msg.id == "utt_1"
    assert msg.chunk_index == 0
    assert msg.text == "hello world"
    assert msg.event == "PART"


def test_pipeline_message_end_event():
    msg = PipelineMessage(
        id="utt_1",
        chunk_index=-1,
        text="",
        event="END_ASR",
        is_final=True,
        end_of_speech_time=12345.6,
    )
    assert msg.event == "END_ASR"
    assert msg.is_final is True
    assert msg.end_of_speech_time == 12345.6


def test_pipeline_message_validation_error():
    with pytest.raises(Exception):
        PipelineMessage(
            id=None,   # invalid
            chunk_index="wrong",  # invalid
            text="hello",
            event="PART"
        )
