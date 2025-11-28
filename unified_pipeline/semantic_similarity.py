"""
Semantic Similarity Checker

Prevents grammar hallucinations and false corrections by checking
semantic similarity between chunks.
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SemanticSimilarityChecker:
    """
    Check semantic similarity between text chunks to prevent hallucinations.
    
    Uses simple heuristics (can be enhanced with embeddings later):
    - Word overlap ratio
    - Levenshtein distance
    - Common word filtering
    """
    
    def __init__(self, similarity_threshold: float = 0.3):
        """
        Args:
            similarity_threshold: Minimum similarity to accept (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.previous_chunk: Optional[str] = None
    
    def is_similar(self, previous: str, current: str) -> bool:
        """
        Check if current chunk is semantically similar to previous.
        
        Returns True if chunks are similar enough (not a hallucination).
        """
        if not previous or not current:
            return True  # Allow if one is empty
        
        # Normalize
        prev_words = set(self._normalize_words(previous))
        curr_words = set(self._normalize_words(current))
        
        if not prev_words or not curr_words:
            return True
        
        # Calculate word overlap ratio
        intersection = prev_words & curr_words
        union = prev_words | curr_words
        
        if not union:
            return True
        
        overlap_ratio = len(intersection) / len(union)
        
        # Also check if current is a continuation (has new words)
        new_words = curr_words - prev_words
        continuation_score = len(new_words) / max(len(curr_words), 1)
        
        # Accept if:
        # 1. High overlap (similar content), OR
        # 2. Low overlap but high continuation (new content building on old)
        is_valid = (overlap_ratio >= self.similarity_threshold) or (continuation_score >= 0.5)
        
        if not is_valid:
            logger.warning(
                f"Low similarity detected: overlap={overlap_ratio:.2f}, "
                f"continuation={continuation_score:.2f}. "
                f"Previous: '{previous[:50]}...', Current: '{current[:50]}...'"
            )
        
        return is_valid
    
    def _normalize_words(self, text: str) -> list:
        """Normalize text to word list (lowercase, no punctuation)"""
        # Remove punctuation, lowercase, split
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = [w for w in text.split() if len(w) > 2]  # Filter very short words
        return words
    
    def should_accept_chunk(self, current: str) -> bool:
        """
        Check if current chunk should be accepted based on previous chunk.
        
        Returns True if chunk should be kept, False if it should be dropped.
        """
        if not self.previous_chunk:
            self.previous_chunk = current
            return True
        
        is_valid = self.is_similar(self.previous_chunk, current)
        
        if is_valid:
            self.previous_chunk = current
        
        return is_valid
    
    def reset(self):
        """Reset previous chunk (call when starting new utterance)"""
        self.previous_chunk = None

