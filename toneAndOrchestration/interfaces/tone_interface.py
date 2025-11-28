# interfaces/tone_interface.py
from abc import ABC, abstractmethod
from schemas.pipeline_message import PipelineMessage


class ToneInterface(ABC):
    """
    Contract for the Tone Transformation + Orchestration stage.
    This is what the orchestrator will call.
    """

    @abstractmethod
    def process_chunk(self, message: PipelineMessage) -> PipelineMessage:
        """
        Called for every PART chunk from the grammar module.
        Should optionally tone-transform and return a PipelineMessage.
        """
        pass

    @abstractmethod
    def finalize(self, utterance_id: str) -> PipelineMessage:
        """
        Called when END_GRAMMAR event arrives.
        Should assemble all chunks and produce a final END_TONE message.
        """
        pass
