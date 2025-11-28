from fastapi import WebSocket, WebSocketDisconnect
import numpy as np
from shared.types import TranscriptChunk
from .audio_capture import AudioBuffer
from .whisper_engine import WhisperASREngine

asr_engine = WhisperASREngine()

async def asr_stream(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = AudioBuffer()  # Create new buffer per connection
    chunk_counter = 0
    
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            audio_buffer.add_chunk(audio_chunk)
            
            chunk_counter += 1
            
            # Transcribe every 2 seconds of audio (about 20 chunks at 100ms each)
            if chunk_counter >= 20 and len(audio_buffer.buffer) > audio_buffer.chunk_samples:
                chunk_counter = 0
                
                # Get current buffer content
                buffer_array = np.array(list(audio_buffer.buffer), dtype=np.float32)
                
                # Only transcribe if we have enough audio data
                if len(buffer_array) > 0:
                    # Transcribe
                    transcript, metadata = asr_engine.transcribe(buffer_array)
                    
                    if transcript.strip():  # Only send non-empty transcripts
                        chunk = TranscriptChunk(
                            raw_text=transcript,
                            confidence=metadata['confidence'],
                            duration_ms=metadata['latency_ms']
                        )
                        
                        await websocket.send_json(chunk.to_dict())
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
        try:
            await websocket.send_json({'error': str(e)})
        except:
            pass
