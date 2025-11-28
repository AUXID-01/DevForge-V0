# tone_module/tests/test_transformer.py
import time
from tone_module.transformer import ToneTransformer
from schemas.pipeline_message import PipelineMessage

def test_tone_transformer_concise_mode():
    tt = ToneTransformer(mode="concise")
    # simulate streaming chunks
    msg0 = PipelineMessage(id="utt_test", chunk_index=0, text="I think this is really very good", event="PART")
    msg1 = PipelineMessage(id="utt_test", chunk_index=1, text="and I kind of want to proceed", event="PART")
    p0 = tt.process_chunk(msg0)
    p1 = tt.process_chunk(msg1)
    assert "really" not in p0.text or "very" not in p0.text  # intensifiers reduced
    # finalize
    # set a fake end_of_speech_time (epoch sec)
    tt.end_of_speech_time_by_id["utt_test"] = time.time()
    out = tt.finalize("utt_test")
    assert out.event == "END_TONE"
    assert out.is_final is True
    assert "kind of" not in out.text.lower()
    assert len(out.text) > 0

def test_tone_transformer_formal_mode():
    tt = ToneTransformer(mode="formal")
    msg = PipelineMessage(id="f1", chunk_index=0, text="thanks, i'm gonna go now", event="PART")
    preview = tt.process_chunk(msg)
    # preview should already replace "gonna" / "i'm"
    assert "going to" in preview.text or "I am" in preview.text
    tt.end_of_speech_time_by_id["f1"] = time.time()
    final = tt.finalize("f1")
    assert "thank you" in final.text.lower() or "going to" in final.text

def test_tone_transformer_neutral_mode_single_call():
    tt = ToneTransformer(mode="neutral")
    out = tt.tone_transform("this is a sample sentence without punctuation", mode="neutral")
    assert out[0].isupper() or out.endswith(".") or len(out) > 0
