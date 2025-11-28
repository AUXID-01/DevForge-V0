"""
Voice Activity Detection (VAD) using WebRTC VAD
Detects speech presence in audio to prevent transcription of silence
"""

import webrtcvad
import numpy as np
from collections import deque


class VADDetector:
    def __init__(self, sample_rate=16000, frame_duration_ms=30, aggressiveness=2):
        """
        Initialize VAD detector.
        
        Args:
            sample_rate: Audio sample rate (8000, 16000, 32000, or 48000 Hz)
            frame_duration_ms: Frame duration (10, 20, or 30 ms)
            aggressiveness: VAD aggressiveness (0-3, higher = more aggressive filtering)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        
        # Speech detection parameters
        self.speech_frames = deque(maxlen=30)  # Track last 30 frames (~0.9 seconds at 30ms)
        self.speech_ratio_threshold = 0.3  # 30% of frames must contain speech
        
    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if audio chunk contains speech.
        
        Args:
            audio_chunk: Audio data as float32 numpy array
            
        Returns:
            True if speech detected, False otherwise
        """
        # Convert float32 to int16 for WebRTC VAD
        audio_int16 = (audio_chunk * 32768).astype(np.int16)
        
        # Process in frames
        num_frames = len(audio_int16) // self.frame_size
        speech_frame_count = 0
        
        for i in range(num_frames):
            start = i * self.frame_size
            end = start + self.frame_size
            frame = audio_int16[start:end]
            
            # Check if frame size is correct
            if len(frame) == self.frame_size:
                try:
                    is_speech_frame = self.vad.is_speech(frame.tobytes(), self.sample_rate)
                    if is_speech_frame:
                        speech_frame_count += 1
                except Exception:
                    # If VAD fails, assume no speech
                    pass
        
        # Calculate speech ratio
        if num_frames > 0:
            speech_ratio = speech_frame_count / num_frames
            self.speech_frames.append(speech_ratio > 0.3)  # Frame has significant speech
        else:
            self.speech_frames.append(False)
        
        # Check if enough recent frames contain speech
        if len(self.speech_frames) > 0:
            recent_speech_ratio = sum(self.speech_frames) / len(self.speech_frames)
            return recent_speech_ratio >= self.speech_ratio_threshold
        
        return False
    
    def reset(self):
        """Reset VAD state"""
        self.speech_frames.clear()


class SpeechSegmentDetector:
    def __init__(self, sample_rate=16000, silence_duration_ms=2500):
        """
        Detect speech segments and silence periods.
        
        Args:
            sample_rate: Audio sample rate
            silence_duration_ms: Duration of silence to consider speech ended (milliseconds)
                               Default: 2500ms (2.5 seconds) for auto-stop
        """
        self.vad = VADDetector(sample_rate=sample_rate, aggressiveness=2)
        self.sample_rate = sample_rate
        self.silence_duration_ms = silence_duration_ms
        # More accurate frame-based calculation
        frame_duration_ms = 30  # VAD frame duration
        self.silence_frames_threshold = int(silence_duration_ms / frame_duration_ms)  # Convert to number of frames
        
        self.consecutive_silence_frames = 0
        self.is_speaking = False
        self.speech_started = False
        self.silence_duration_seconds = silence_duration_ms / 1000.0
        
    def process_audio(self, audio_chunk: np.ndarray) -> dict:
        """
        Process audio chunk and return speech status.
        
        Args:
            audio_chunk: Audio data as float32 numpy array
            
        Returns:
            dict with keys:
                - has_speech: bool, if current chunk has speech
                - speech_started: bool, if speech just started
                - speech_ended: bool, if speech just ended
                - is_speaking: bool, current speaking state
        """
        has_speech = self.vad.is_speech(audio_chunk)
        speech_started = False
        speech_ended = False
        
        if has_speech:
            # Speech detected
            self.consecutive_silence_frames = 0
            
            if not self.is_speaking:
                # Speech just started
                self.is_speaking = True
                self.speech_started = True
                speech_started = True
        else:
            # No speech detected
            if self.is_speaking:
                self.consecutive_silence_frames += 1
                
                # Check if silence duration exceeded threshold
                if self.consecutive_silence_frames >= self.silence_frames_threshold:
                    # Speech ended
                    self.is_speaking = False
                    self.speech_started = False
                    speech_ended = True
                    self.consecutive_silence_frames = 0
        
        return {
            'has_speech': has_speech,
            'speech_started': speech_started,
            'speech_ended': speech_ended,
            'is_speaking': self.is_speaking
        }
    
    def reset(self):
        """Reset detector state"""
        self.vad.reset()
        self.consecutive_silence_frames = 0
        self.is_speaking = False
        self.speech_started = False
