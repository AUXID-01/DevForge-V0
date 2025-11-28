from tone_module.transformer import ToneTransformer

# -----------------------
# FORMAL MODE TESTS
# -----------------------

def test_formal_expands_contractions():
    t = ToneTransformer(mode="formal")
    out = t._tone_transform("I'm gonna join later, thanks!")
    # Only tone changes; no grammar checks
    assert out == "I am going to join later, thank you!"


def test_formal_reduces_intensifiers():
    t = ToneTransformer(mode="formal")
    out = t._tone_transform("I really really appreciate it.")
    # Concise & polite
    assert out in [
        "I appreciate it.",
        "I truly appreciate it."
    ]

# -----------------------
# CASUAL MODE TESTS
# -----------------------

def test_casual_keeps_contractions():
    t = ToneTransformer(mode="casual")
    out = t._tone_transform("I'm going to join.")
    assert out == "I'm going to join."  # NOT "I am"

def test_casual_simplifies_formal_words():
    t = ToneTransformer(mode="casual")
    out = t._tone_transform("I appreciate your assistance.")
    # Only tone simplification
    assert out == "I appreciate your help."

# -----------------------
# CONCISE MODE TESTS
# -----------------------

def test_concise_removes_intensifiers():
    t = ToneTransformer(mode="concise")
    out = t._tone_transform("I really really appreciate it.")
    assert out == "I appreciate it."

def test_concise_keeps_meaning():
    t = ToneTransformer(mode="concise")
    out = t._tone_transform("I'm going to join later.")
    # Remove fluff, NOT rewrite grammar
    assert out == "I'm going to join later."

# -----------------------
# NEUTRAL MODE TESTS
# -----------------------

def test_neutral_preserves_original_text():
    t = ToneTransformer(mode="neutral")
    text = "I'm gonna join later, thanks!"
    out = t._tone_transform(text)
    assert out == text  # NOTHING should change in neutral mode
