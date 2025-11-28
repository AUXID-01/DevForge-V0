# tone_module/tone_rules.py
"""
Rule-based mappings and sets used by the tone transformer.
Keep these lists/dicts small and editable for rapid iteration.
"""
from typing import Dict, List

# Casual -> Formal (expanded for better transformation)
FORMAL_EXPANSIONS: Dict[str, str] = {
    "wanna": "want to",
    "gonna": "going to",
    "gotta": "have to",
    "kinda": "somewhat",
    "sorta": "somewhat",
    "yeah": "yes",
    "yep": "yes",
    "nope": "no",
    "ok": "okay",
    "ok?": "okay?",
    "thanks": "thank you",
    "thanks!": "thank you!",
    "i'm": "I am",
    "it's": "It is",
    "don't": "do not",
    "can't": "cannot",
    "won't": "will not",
    "we're": "we are",
    "i'll": "I will",
    "you're": "you are",
    "they're": "they are",
    "that's": "that is",
    "what's": "what is",
    "there's": "there is",
    "here's": "here is",
    "let's": "let us",
    "i've": "I have",
    "you've": "you have",
    "we've": "we have",
    "i'd": "I would",
    "you'd": "you would",
    "gimme": "give me",
    "lemme": "let me",
    "gonna": "going to",
    "wanna": "want to",
}

# Formal -> Casual (examples)
CASUAL_SIMPLIFICATIONS: Dict[str, str] = {
    "do not": "don't",
    "cannot": "can't",
    "assistance": "help",
    "assisting": "helping",
    "I am": "I'm",
    "It is": "It's",
    "thank you": "thanks",
    "yes.": "yeah.",
    "Yes.": "Yeah.",
}

# Hedging/softening phrases to consider removing for Formal/Concise modes
HEDGES: List[str] = [
    "kind of",
    "sort of",
    "i think",
    "i believe",
    "i guess",
    "i mean",
    "you know",
    "to be honest",
    "actually",
    "basically",
    "literally",
    "just",
    "maybe",
    "perhaps",
    "probably",
    "possibly",
    "i suppose",
    "i assume",
    "i feel like",
    "it seems like",
    "it looks like",
]

# Filler words (should generally be removed by cleaner earlier, but tone module can guard)
FILLERS: List[str] = [
    "um", "uh", "erm", "hmm", "ah", "mm", "you know", "like"
]

# Adverb intensifiers that concise mode might reduce
INTENSIFIERS: List[str] = [
    "very", "extremely", "really", "super", "quite"
]

# Short list of polite phrase expansions for Formal mode
FORMAL_POLITE_MAP: Dict[str, str] = {
    "thanks for": "thank you for",
    "thanks to": "thank you to",
    "thanks": "thank you",
}

# Modes supported
SUPPORTED_MODES = {"formal", "casual", "concise", "neutral"}
