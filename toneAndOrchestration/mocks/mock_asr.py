# mocks/mock_asr.py
from typing import List
from schemas.pipeline_message import PipelineMessage


def mock_asr_stream(utt_id: str) -> List[PipelineMessage]:
    """
    Simulate ASR output for one utterance as streaming chunks.
    Includes a small repetition and fillers for downstream modules to fix.
    """
    chunks = [
        PipelineMessage(
            id=utt_id,
            chunk_index=0,
            text="um I I really want to",
            event="PART",
            is_final=False,
            end_of_speech_time=None,
        ),
        PipelineMessage(
            id=utt_id,
            chunk_index=1,
            text="thank you for coming you know",
            event="PART",
            is_final=False,
            end_of_speech_time=None,
        ),
        PipelineMessage(
            id=utt_id,
            chunk_index=2,
            text="this is like really important",
            event="PART",
            is_final=False,
            end_of_speech_time=None,
        ),
    ]

    # End of speech marker with end_of_speech_time
    end_msg = PipelineMessage(
        id=utt_id,
        chunk_index=-1,
        text="",
        event="END_ASR",
        is_final=True,
        end_of_speech_time=None,  # can be filled later by test or orchestrator
    )

    return chunks + [end_msg]
