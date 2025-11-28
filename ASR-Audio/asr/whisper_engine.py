import whisper
import numpy as np
import time

class WhisperASREngine:
    def __init__(self, model_name="base.en"):
        """
        Initialize OpenAI Whisper with English-specific model for best accuracy.
        Model: base.en - optimized for English, very accurate
        """
        self.model = whisper.load_model(model_name)
        self.all_tokens = []  # Store all previous tokens for context
        self.prompt_reset_since = 0
        self.lucid_threshold = 0.3  # Threshold to determine permissible chunk length for healthy transcript
        self.seek = 0  # Current position in audio
        self.N_FRAMES = whisper.audio.N_FRAMES  # Standard Whisper frame size (3000 frames = 30 seconds)
        print(f"Loaded Whisper {model_name} model with lucid threshold anti-hallucination")
    
    def transcribe(self, audio: np.ndarray) -> tuple[str, dict]:
        start_time = time.time()
        
        # Check if audio has enough energy
        rms = np.sqrt(np.mean(audio**2))
        if rms < 0.005:
            return ("", {
                'latency_ms': 0,
                'confidence': 0.0,
                'language': 'en',
                'no_speech_prob': 1.0
            })
        
        # Normalize audio
        audio = audio.astype(np.float32)
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        
        # Pad if too short
        min_samples = 8000
        if len(audio) < min_samples:
            audio = np.pad(audio, (0, min_samples - len(audio)))
        
        # Convert audio to Whisper's expected format (30 second chunks)
        num_frames = len(audio) // 160  # Whisper uses 160 samples per frame at 16kHz
        
        # Calculate lucid score for context management
        lucid_score = 1.0
        decode_options = {
            "language": "en",
            "task": "transcribe",
            "temperature": 0.0,
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "condition_on_previous_text": False,
        }
        
        # Calculate lucid score based on chunk position
        # First chunk or within bounds
        if ((self.seek + self.N_FRAMES) / num_frames < 1.0) or (self.seek == 0):
            lucid_score = 1.0
        else:
            # Last chunk - calculate score based on remaining frames
            lucid_score = (num_frames - self.seek) / self.N_FRAMES
        
        # If lucid_score is below threshold, disable context to avoid hallucinations
        if lucid_score < self.lucid_threshold:
            decode_options["condition_on_previous_text"] = False
        else:
            # Allow Whisper to use previous context for better accuracy
            decode_options["condition_on_previous_text"] = True
        
        # Transcribe with optimized settings
        result = self.model.transcribe(
            audio,
            **decode_options
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Get confidence and update token history
        segments = result.get('segments', [])
        confidence = 1.0
        no_speech_prob = 0.0
        
        if segments and len(segments) > 0:
            no_speech_prob = segments[0].get('no_speech_prob', 0.0)
            confidence = 1.0 - no_speech_prob
            
            # Update token history for future context (only if high confidence)
            if confidence > 0.5:
                for segment in segments:
                    if 'tokens' in segment:
                        self.all_tokens.extend(segment['tokens'])
                
                # Keep only last 200 tokens to prevent context overflow
                if len(self.all_tokens) > 200:
                    self.all_tokens = self.all_tokens[-200:]
                    self.prompt_reset_since = 0
        
        text = result['text'].strip()
        
        # Update seek position for next chunk
        self.seek += len(audio) // 160
        
        # Reset seek if we've processed a complete session
        if self.seek >= num_frames:
            self.seek = 0
        
        return (text, {
            'latency_ms': latency_ms,
            'confidence': confidence,
            'language': 'en',
            'no_speech_prob': no_speech_prob,
            'lucid_score': lucid_score
        })
    
    def reset_context(self):
        """Reset the token history and seek position for a new session"""
        self.all_tokens = []
        self.prompt_reset_since = 0
        self.seek = 0
