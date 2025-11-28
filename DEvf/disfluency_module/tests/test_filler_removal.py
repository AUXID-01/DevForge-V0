# disfluency_module/tests/test_filler_removal.py

from disfluency_module import process

def test_basic_filler_removal():
    raw = "um I was like thinking that uh we could maybe go"
    out = process(raw)
    
    cleaned = out["cleaned_text"].lower()
    
    # Check fillers are removed
    assert "um" not in cleaned
    assert "like" not in cleaned
    assert "uh" not in cleaned
    
    # Check meaningful words remain
    assert "thinking" in cleaned
    assert "could" in cleaned
    assert "go" in cleaned

def test_repetition_removal():
    raw = "I I want want to to go"
    out = process(raw)
    
    cleaned = out["cleaned_text"]
    
    # Simple consecutive duplicate removal
    assert cleaned == "I want to go"

def test_combined():
    raw = "um I I was like thinking that uh we we could go"
    out = process(raw)
    
    cleaned = out["cleaned_text"].lower()
    
    # Fillers removed
    assert "um" not in cleaned
    assert "uh" not in cleaned
    assert "like" not in cleaned
    
    # Repetitions removed (consecutive duplicates)
    # Should be roughly "i was thinking that we could go"
    assert "thinking" in cleaned
    assert "could" in cleaned
