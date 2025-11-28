"""
Rolling Window Deduplication Algorithm

Prevents overlapping text, duplications, and out-of-order fragments
by using a rolling window to detect and remove overlaps.
"""

import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RollingWindowDeduplicator:
    """
    Rolling window deduplication to prevent chunk overlap issues.
    
    Keeps a buffer of the last N characters and removes overlapping
    text from new chunks.
    """
    
    def __init__(self, window_size: int = 60):
        """
        Args:
            window_size: Number of characters to keep in rolling window (default: 60)
        """
        self.window_size = window_size
        self.buffer: str = ""
    
    def deduplicate(self, new_chunk: str) -> Tuple[str, bool]:
        """
        Remove overlapping text from new chunk.
        
        Args:
            new_chunk: New text chunk that may overlap with previous text
            
        Returns:
            Tuple of (deduplicated_chunk, has_overlap)
        """
        if not new_chunk or not new_chunk.strip():
            return new_chunk, False
        
        new_chunk = new_chunk.strip()
        
        # If buffer is empty, just add to buffer
        if not self.buffer:
            self.buffer = new_chunk[-self.window_size:] if len(new_chunk) > self.window_size else new_chunk
            return new_chunk, False
        
        # Find overlap between buffer and new chunk
        overlap = self._find_overlap(self.buffer, new_chunk)
        
        if overlap:
            # Remove overlapping part from new chunk
            deduplicated = new_chunk[len(overlap):].strip()
            
            # Update buffer with new content
            combined = self.buffer + deduplicated
            self.buffer = combined[-self.window_size:] if len(combined) > self.window_size else combined
            
            logger.debug(f"Overlap detected: '{overlap}' removed, new text: '{deduplicated}'")
            return deduplicated, True
        else:
            # No overlap, append normally
            combined = self.buffer + " " + new_chunk
            self.buffer = combined[-self.window_size:] if len(combined) > self.window_size else combined
            return new_chunk, False
    
    def _find_overlap(self, buffer: str, new_chunk: str) -> Optional[str]:
        """
        Find overlap between last 30 chars of buffer and first 30 chars of new chunk.
        
        This is the key fix - compare last 30 chars of buffer with first 30 chars of new chunk.
        """
        if not buffer or not new_chunk:
            return None
        
        # Normalize whitespace
        buffer = re.sub(r'\s+', ' ', buffer.strip())
        new_chunk = re.sub(r'\s+', ' ', new_chunk.strip())
        
        # Get last 30 chars of buffer and first 30 chars of new chunk
        buffer_tail = buffer[-30:].lower().strip()
        new_head = new_chunk[:30].lower().strip()
        
        if not buffer_tail or not new_head:
            return None
        
        # Try to find overlap starting from longest possible match
        # Check word-level first (more accurate)
        buffer_words = buffer_tail.split()
        new_words = new_head.split()
        
        # Check for word-level overlap (at least 2 words)
        max_overlap_words = min(len(buffer_words), len(new_words), 8)
        
        for overlap_len in range(max_overlap_words, 1, -1):  # At least 2 words
            if overlap_len > len(buffer_words) or overlap_len > len(new_words):
                continue
                
            buffer_tail_words = ' '.join(buffer_words[-overlap_len:])
            new_head_words = ' '.join(new_words[:overlap_len])
            
            if buffer_tail_words == new_head_words:
                # Found exact word match - return the original case version
                original_new_head = ' '.join(new_chunk.split()[:overlap_len])
                return original_new_head
        
        # Fallback: character-level overlap
        # Try different lengths from 30 down to 5
        for i in range(min(30, len(new_chunk)), 4, -1):
            new_head_sub = new_chunk[:i].lower()
            if buffer_tail.endswith(new_head_sub):
                # Found character-level overlap
                return new_chunk[:i]
            # Also check if new_head_sub appears at the end of buffer_tail
            if new_head_sub in buffer_tail and len(new_head_sub) >= 10:
                # Partial match - return it
                return new_chunk[:i]
        
        return None
    
    def reset(self):
        """Reset the buffer (call when starting new utterance)"""
        self.buffer = ""
    
    def get_buffer(self) -> str:
        """Get current buffer content (for debugging)"""
        return self.buffer

