# tone_module/tests/test_utils.py
from tone_module.utils import expand_contractions, apply_mapping, normalize_whitespace

def test_expand_contractions_simple():
    s = "I'm fine. Don't worry."
    out = expand_contractions(s)
    assert "I am" in out or "do not" in out

def test_apply_mapping_case_preserve():
    mapping = {"thanks": "thank you"}
    out = apply_mapping("Thanks for your help", mapping)
    assert "Thank you" in out

def test_normalize_whitespace():
    s = "this   has   extra   spaces"
    assert normalize_whitespace(s) == "this has extra spaces"
