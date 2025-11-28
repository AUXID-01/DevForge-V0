from typing import Dict, Optional


class UtteranceState:
    """
    Holds all intermediate data for a single utterance.
    Used by the orchestrator to store chunks until END_GRAMMAR.
    """

    def __init__(self):
        self.chunks: Dict[int, str] = {}          # chunk_index -> text
        self.end_of_speech_time: Optional[float] = None
        self.received_end_grammar: bool = False

    def add_chunk(self, index: int, text: str):
        self.chunks[index] = text

    def mark_end_grammar(self, eos_time: float):
        self.received_end_grammar = True
        self.end_of_speech_time = eos_time

    def assemble_full_text(self) -> str:
        """
        Assemble full text from chunks in correct order.
        Filters out empty chunks and ensures proper ordering.
        """
        if not self.chunks:
            return ""
        
        # Get all chunk indices and sort them
        sorted_indices = sorted([idx for idx in self.chunks.keys() if idx >= 0])  # Only positive indices
        
        # Collect non-empty chunks in order
        ordered_chunks = []
        for idx in sorted_indices:
            text = self.chunks[idx]
            if text and text.strip():  # Only add non-empty chunks
                ordered_chunks.append(text.strip())
        
        # Join with spaces and clean up
        full_text = " ".join(ordered_chunks).strip()
        
        # Remove duplicate consecutive words/phrases
        words = full_text.split()
        if len(words) > 1:
            cleaned_words = [words[0]]
            for i in range(1, len(words)):
                # Don't add if it's the same as previous word
                if words[i].lower() != words[i-1].lower():
                    cleaned_words.append(words[i])
            full_text = " ".join(cleaned_words)
        
        return full_text
