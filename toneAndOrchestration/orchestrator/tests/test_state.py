# orchestrator/tests/test_state.py

from orchestrator.state import UtteranceState


def test_utterance_state_add_and_assemble():
    st = UtteranceState()
    st.add_chunk(1, "world")
    st.add_chunk(0, "hello")

    full = st.assemble_full_text()
    # must respect chunk_index ordering
    assert full == "hello world"


def test_utterance_state_end_grammar_flag_and_time():
    st = UtteranceState()
    assert st.received_end_grammar is False
    assert st.end_of_speech_time is None

    st.mark_end_grammar(123.45)

    assert st.received_end_grammar is True
    assert st.end_of_speech_time == 123.45
