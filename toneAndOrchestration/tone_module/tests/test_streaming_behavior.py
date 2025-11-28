from tone_module.transformer import ToneTransformer
from schemas.pipeline_message import PipelineMessage

def test_streaming_formal_preview():
    t = ToneTransformer(mode="formal")

    chunk1 = PipelineMessage(
        id="utt1", chunk_index=0, text="I'm gonna join", event="PART"
    )
    chunk2 = PipelineMessage(
        id="utt1", chunk_index=1, text="later thanks", event="PART"
    )

    out1 = t.process_chunk(chunk1)
    out2 = t.process_chunk(chunk2)

    assert out1.text == "I am going to join"
    assert out2.text == "later thank you"

def test_streaming_final_assembly():
    t = ToneTransformer(mode="formal")

    # simulate chunks
    t.process_chunk(PipelineMessage(id="u1", chunk_index=0, text="I'm gonna join", event="PART"))
    t.process_chunk(PipelineMessage(id="u1", chunk_index=1, text="later thanks", event="PART"))

    # simulate END from grammar stage
    final = t.finalize("u1")

    assert final.text == "I am going to join later thank you."
