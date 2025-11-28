from fastapi import FastAPI, WebSocket, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import numpy as np
from asr.endpoint import asr_stream
from asr.endpoint_queue import asr_stream_with_queue, asr_stream_with_silence_detection
from asr.whisper_engine import WhisperASREngine

app = FastAPI(title="ASR Pipeline")
asr_engine = WhisperASREngine()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.websocket("/asr/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Original endpoint - simple real-time transcription"""
    await asr_stream(websocket)

@app.websocket("/asr/stream/queue")
async def websocket_queue_endpoint(websocket: WebSocket):
    """Queue-based endpoint with PipelineMessage schema"""
    await asr_stream_with_queue(websocket)

@app.websocket("/asr/stream/silence")
async def websocket_silence_endpoint(websocket: WebSocket):
    """Queue-based endpoint with automatic END_ASR on silence"""
    await asr_stream_with_silence_detection(websocket)

@app.post("/asr/file")
async def asr_file(audio_file: UploadFile):
    contents = await audio_file.read()
    audio = np.frombuffer(contents, dtype=np.float32)
    transcript, metadata = asr_engine.transcribe(audio)
    
    return {
        "transcript": transcript,
        "latency_ms": metadata['latency_ms'],
        "confidence": metadata['confidence']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
