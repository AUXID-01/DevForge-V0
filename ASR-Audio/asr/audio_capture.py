import sounddevice as sd
import numpy as np
from collections import deque
from dataclasses import dataclass

@dataclass
class AudioBuffer:
    sample_rate: int = 16000
    chunk_duration_ms: int = 100
    channels: int = 1
    
    def __post_init__(self):
        self.chunk_samples = (self.sample_rate * self.chunk_duration_ms) // 1000
        self.buffer = deque(maxlen=int(self.sample_rate * 30))  # 30s max
        self.silence_threshold = 0.01
        self.silence_counter = 0
        self.max_silence_frames = 30  # 3s silence = END
    
    def add_chunk(self, chunk: np.ndarray) -> np.ndarray | None:
        self.buffer.extend(chunk.flatten())
        
        rms = np.sqrt(np.mean(chunk**2))
        if rms < self.silence_threshold:
            self.silence_counter += 1
        else:
            self.silence_counter = 0
        
        if self.silence_counter >= self.max_silence_frames:
            self.silence_counter = 0
            if len(self.buffer) > self.chunk_samples:
                return np.array(list(self.buffer), dtype=np.float32)
        return None
    
    def clear(self):
        self.buffer.clear()
        self.silence_counter = 0
