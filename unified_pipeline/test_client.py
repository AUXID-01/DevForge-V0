"""
Simple test client for the unified pipeline

Usage:
    python test_client.py
"""

import asyncio
import websockets
import numpy as np
import json
import sys
from pathlib import Path

# Add ASR-Audio for audio capture if needed
sys.path.insert(0, str(Path(__file__).parent.parent / "ASR-Audio"))


async def test_pipeline_with_mock_audio(tone_mode="neutral"):
    """Test pipeline with mock audio data"""
    uri = f"ws://localhost:8003/pipeline/stream?tone_mode={tone_mode}"
    
    print(f"Connecting to {uri}...")
    print(f"Tone mode: {tone_mode}")
    print("=" * 60)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            print("\nSending mock audio chunks...")
            
            # Send a few mock audio chunks (simulating speech)
            for i in range(5):
                # Generate mock audio (0.1s chunks at 16kHz)
                audio_chunk = np.random.randn(1600).astype(np.float32) * 0.1
                await websocket.send(audio_chunk.tobytes())
                print(f"  Sent chunk {i+1}/5")
                await asyncio.sleep(0.1)
            
            print("\nWaiting for responses...")
            print("-" * 60)
            
            # Receive responses
            response_count = 0
            async for message in websocket:
                data = json.loads(message)
                response_count += 1
                
                event = data.get('event', 'UNKNOWN')
                text = data.get('text', '')
                chunk_idx = data.get('chunk_index', -1)
                
                if event == 'PART':
                    print(f"[PART {chunk_idx}] {text[:80]}...")
                elif event == 'PREVIEW_TONE':
                    print(f"[PREVIEW_TONE {chunk_idx}] {text[:80]}...")
                elif event == 'END_TONE':
                    print("\n" + "=" * 60)
                    print("🎉 FINAL OUTPUT:")
                    print("=" * 60)
                    print(text)
                    print("=" * 60)
                    if data.get('end_of_speech_time'):
                        print(f"\nEnd of speech time: {data['end_of_speech_time']}ms")
                    break
                else:
                    print(f"[{event}] {text}")
            
            print(f"\n✅ Received {response_count} messages")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Is the server running?")
        print("   Start it with: python unified_pipeline/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_pipeline_with_real_audio(tone_mode="neutral"):
    """Test pipeline with real audio capture (if available)"""
    try:
        from asr.audio_capture import AudioCapture
        
        uri = f"ws://localhost:8003/pipeline/stream?tone_mode={tone_mode}"
        
        print(f"Connecting to {uri}...")
        print(f"Tone mode: {tone_mode}")
        print("=" * 60)
        print("Recording audio... (Press Ctrl+C to stop)")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Start audio capture
            capture = AudioCapture()
            capture.start()
            
            try:
                # Send audio chunks
                async def send_audio():
                    while True:
                        chunk = capture.read_chunk()
                        if chunk is not None:
                            await websocket.send(chunk.tobytes())
                        await asyncio.sleep(0.01)
                
                # Receive responses
                async def receive_responses():
                    async for message in websocket:
                        data = json.loads(message)
                        event = data.get('event', 'UNKNOWN')
                        text = data.get('text', '')
                        
                        if event == 'PART':
                            print(f"[PART] {text[:60]}...")
                        elif event == 'PREVIEW_TONE':
                            print(f"[PREVIEW] {text[:60]}...")
                        elif event == 'END_TONE':
                            print("\n" + "=" * 60)
                            print("🎉 FINAL OUTPUT:")
                            print("=" * 60)
                            print(text)
                            print("=" * 60)
                            break
                
                # Run both tasks
                await asyncio.gather(
                    send_audio(),
                    receive_responses()
                )
            finally:
                capture.stop()
                
    except ImportError:
        print("Audio capture not available, using mock audio instead...")
        await test_pipeline_with_mock_audio(tone_mode)
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test unified pipeline")
    parser.add_argument(
        "--tone-mode",
        choices=["neutral", "formal", "casual", "concise"],
        default="neutral",
        help="Tone mode for transformation"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock audio instead of real microphone"
    )
    
    args = parser.parse_args()
    
    if args.mock:
        asyncio.run(test_pipeline_with_mock_audio(args.tone_mode))
    else:
        asyncio.run(test_pipeline_with_real_audio(args.tone_mode))


if __name__ == "__main__":
    main()

