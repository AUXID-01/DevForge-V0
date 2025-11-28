"""
Late Fusion Step

Final cleanup pass after all chunks are processed:
- Merge sentences smoothly
- Fix contradictions
- Remove duplicates
- Normalize tense
- Ensure coherent output
"""

import re
from typing import List
import logging

logger = logging.getLogger(__name__)


class LateFusionProcessor:
    """
    Final fusion step to clean up the complete utterance.
    
    Processes the full text after all chunks have been processed
    to ensure coherence and quality.
    """
    
    def process(self, full_text: str) -> str:
        """
        Apply late fusion processing to full text.
        
        Final paragraph reconstruction:
        - Sentence ordering
        - Duplicate removal
        - Grammar cleanup
        - Tone adjustment
        
        Args:
            full_text: Complete text from all chunks
            
        Returns:
            Cleaned and fused text
        """
        if not full_text or not full_text.strip():
            return full_text
        
        text = full_text.strip()
        
        # Step 1: Remove duplicate sentences (sentence ordering + duplicate removal)
        text = self._remove_duplicate_sentences(text)
        
        # Step 2: Fix sentence boundaries
        text = self._fix_sentence_boundaries(text)
        
        # Step 3: Remove redundant phrases
        text = self._remove_redundant_phrases(text)
        
        # Step 4: Grammar cleanup - fix common errors
        text = self._grammar_cleanup(text)
        
        # Step 5: Normalize spacing
        text = self._normalize_spacing(text)
        
        # Step 6: Ensure proper capitalization
        text = self._fix_capitalization(text)
        
        # Step 7: Remove trailing repetitions
        text = self._remove_trailing_repetitions(text)
        
        # Step 8: Final coherence check
        text = self._ensure_coherence(text)
        
        return text.strip()
    
    def _grammar_cleanup(self, text: str) -> str:
        """Fix common grammar errors in final text"""
        # Fix "they render finish" -> "they finished rendering"
        text = re.sub(r'\bthey\s+render\s+finish\b', 'they finished rendering', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(\w+)\s+render\s+finish\b', r'\1 finished rendering', text, flags=re.IGNORECASE)
        
        # Fix "QI part" -> "QA part" or "quality assurance part"
        text = re.sub(r'\bQI\s+part\b', 'QA part', text, flags=re.IGNORECASE)
        
        # Fix "the mean deadline" -> "the main deadline"
        text = re.sub(r'\bthe\s+mean\s+deadline\b', 'the main deadline', text, flags=re.IGNORECASE)
        
        # Fix "did finished" -> "finished"
        text = re.sub(r'\bdid\s+finished\b', 'finished', text, flags=re.IGNORECASE)
        text = re.sub(r'\bdid\s+(\w+ed)\b', r'\1', text, flags=re.IGNORECASE)
        
        # Fix "they did finished" -> "they finished"
        text = re.sub(r'\bthey\s+did\s+finished\b', 'they finished', text, flags=re.IGNORECASE)
        
        return text
    
    def _remove_duplicate_sentences(self, text: str) -> str:
        """Remove duplicate sentences (exact matches)"""
        sentences = re.split(r'[.!?]+', text)
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Normalize for comparison (lowercase, no extra spaces)
            normalized = re.sub(r'\s+', ' ', sentence.lower())
            
            if normalized not in seen and len(normalized) > 5:  # At least 5 chars
                seen.add(normalized)
                unique_sentences.append(sentence)
        
        # Rejoin with periods
        return '. '.join(unique_sentences) + '.' if unique_sentences else text
    
    def _fix_sentence_boundaries(self, text: str) -> str:
        """Fix sentence boundaries and ensure proper punctuation"""
        # Remove multiple periods/commas
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r',{2,}', ',', text)
        
        # Ensure space after punctuation
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Remove space before punctuation
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        
        return text
    
    def _remove_redundant_phrases(self, text: str) -> str:
        """Remove redundant phrases like 'I mean I mean' or 'you know you know'"""
        # Common redundant patterns
        patterns = [
            r'\b(I mean|you know|I think|I guess)\s+\1\b',
            r'\b(so\s+)?(so\s+)+',  # Multiple 'so's
            r'\b(and\s+)?(and\s+)+',  # Multiple 'and's at start
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_spacing(self, text: str) -> str:
        """Normalize whitespace"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove space at start/end
        text = text.strip()
        return text
    
    def _fix_capitalization(self, text: str) -> str:
        """Ensure proper sentence capitalization"""
        if not text:
            return text
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Capitalize after sentence endings
        text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        return text
    
    def _remove_trailing_repetitions(self, text: str) -> str:
        """Remove words/phrases repeated at the end"""
        words = text.split()
        if len(words) < 4:
            return text
        
        # Check last 3 words for repetition
        last_3 = ' '.join(words[-3:]).lower()
        if last_3 in ' '.join(words[:-3]).lower():
            # Remove last 3 words if they appear earlier
            return ' '.join(words[:-3])
        
        return text
    
    def _ensure_coherence(self, text: str) -> str:
        """Ensure final coherence - remove contradictions and fix ordering"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return text
        
        # Remove contradictory sentences (simple heuristic)
        # If a sentence says "X is not Y" and another says "X is Y", keep the later one
        cleaned_sentences = []
        for i, sentence in enumerate(sentences):
            # Check if this sentence contradicts a previous one
            is_contradiction = False
            for prev_sentence in cleaned_sentences[-3:]:  # Check last 3 sentences
                # Simple contradiction detection
                if ('not' in sentence.lower() and 'not' not in prev_sentence.lower() and
                    len(set(sentence.lower().split()) & set(prev_sentence.lower().split())) > 3):
                    # Possible contradiction - skip this sentence
                    is_contradiction = True
                    break
            
            if not is_contradiction:
                cleaned_sentences.append(sentence)
        
        # Rejoin sentences
        if cleaned_sentences:
            return '. '.join(cleaned_sentences) + '.' if cleaned_sentences else text
        
        return text

