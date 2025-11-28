"""
Non-LLM Tone/Style Transformation
Pure template-based + substitution rules
"""

import re

class ToneTransformer:
    """
    Transform text tone WITHOUT any ML/LLM.
    Use only dictionary substitution + grammar rules.
    """
    
    def __init__(self):
        self.tone_rules = {
            'formal': {
                # Simplifications → formal versions
                "don't": "do not",
                "can't": "cannot",
                "won't": "will not",
                "gonna": "will",
                "wanna": "want to",
                "ya": "you",
                "gotta": "must",
                "kinda": "somewhat",
                "sorta": "rather",
                # Casual → formal
                "yeah": "yes",
                "nope": "no",
                "btw": "by the way",
                "asap": "as soon as possible",
                # Remove filler phrases
                "you know": "",
                "like": "",
                "I mean": "",
            },
            'casual': {
                # Formal → casual
                "do not": "don't",
                "cannot": "can't",
                "will not": "won't",
                "must": "gotta",
                "somewhat": "kinda",
                "rather": "sorta",
                # Add casual markers
                "hello": "hey",
                "goodbye": "bye",
            },
            'concise': {
                # Remove unnecessary words
                "I think that": "I think",
                "It is very": "It's very",
                "in order to": "to",
                "due to the fact that": "because",
                "at this point in time": "now",
                "for the purpose of": "to",
            },
            'neutral': {
                # Keep standard English
            }
        }
    
    def transform(self, text: str, mode: str = 'neutral') -> str:
        """Transform text to target tone using only rules"""
        if mode not in self.tone_rules:
            return text
        
        result = text
        rules = self.tone_rules[mode]
        
        # Apply substitutions (case-insensitive)
        for pattern, replacement in rules.items():
            # Use word boundaries to avoid partial matches
            regex_pattern = r'\b' + re.escape(pattern) + r'\b'
            result = re.sub(regex_pattern, replacement, result, flags=re.IGNORECASE)
        
        # Clean up double spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result


# Test
if __name__ == "__main__":
    transformer = ToneTransformer()
    
    text = "I think that you know we should like definitely do not go because I mean it's kinda wrong"
    
    for tone in ['formal', 'casual', 'concise', 'neutral']:
        transformed = transformer.transform(text, tone)
        print(f"\n{tone.upper()}:")
        print(f"  {transformed}")
