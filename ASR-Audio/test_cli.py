#!/usr/bin/env python3
"""
Test script to create a sample audio file using text-to-speech
and then transcribe it using the CLI tool
"""

import numpy as np
import subprocess
import wave
import sys

def create_test_audio(filename="test_audio/sample.wav", duration=3.0, sample_rate=16000):
    """
    Create a simple test audio file with a sine wave pattern
    This simulates an audio file for testing the CLI
    """
    print(f"Creating test audio file: {filename}")
    
    # Generate a simple sine wave tone (440 Hz - A note)
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440.0
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Add some amplitude modulation to make it more interesting
    modulation = 0.5 * (1 + np.sin(2 * np.pi * 2 * t))
    audio_data = audio_data * modulation
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"✓ Created {filename} ({duration}s, {sample_rate}Hz)")
    return filename

def main():
    print("=" * 60)
    print("Whisper CLI Test Script")
    print("=" * 60)
    print()
    
    # Create test audio file
    audio_file = create_test_audio()
    
    print()
    print("Now you can test the CLI with this audio file:")
    print()
    print(f"  python cli_transcribe.py {audio_file}")
    print(f"  python cli_transcribe.py {audio_file} --model tiny")
    print(f"  python cli_transcribe.py {audio_file} --model medium --verbose")
    print()
    print("Note: Since this is a sine wave tone, Whisper may not")
    print("detect speech, but it demonstrates the CLI workflow.")
    print()
    print("For real testing, use an actual audio recording with speech.")

if __name__ == "__main__":
    main()
