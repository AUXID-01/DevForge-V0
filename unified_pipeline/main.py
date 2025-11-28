"""
Unified Pipeline Server

Main FastAPI server that provides WebSocket endpoint for the full pipeline:
ASR → Disfluency → Grammar → Tone

Usage:
    python main.py

WebSocket endpoint: ws://localhost:8003/pipeline/stream
"""

import asyncio
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
import uuid
import numpy as np
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ASR-Audio"))
sys.path.insert(0, str(Path(__file__).parent.parent / "DEvf"))
sys.path.insert(0, str(Path(__file__).parent.parent / "speech-dictation-engine" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "toneAndOrchestration"))

from pipeline_orchestrator import UnifiedPipelineOrchestrator
from schemas.pipeline_message import PipelineMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Unified Pipeline Server starting up...")
    logger.info("✅ Server ready")
    yield
    # Shutdown
    logger.info("🛑 Unified Pipeline Server shutting down...")

app = FastAPI(
    title="Unified Speech Dictation Pipeline",
    description="Full pipeline: ASR → Disfluency → Grammar → Tone",
    version="1.0.0",
    lifespan=lifespan
)

# Serve static files (UI)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global orchestrator (will be initialized per session with tone mode)
orchestrators: dict = {}


@app.websocket("/pipeline/stream")
async def pipeline_stream(websocket: WebSocket, tone_mode: str = Query("neutral", pattern="^(neutral|formal|casual|concise)$")):
    """
    WebSocket endpoint for full pipeline streaming.
    
    Query params:
        tone_mode: One of "neutral", "formal", "casual", "concise" (default: "neutral")
    
    Input: Audio chunks as bytes (float32 numpy array)
    Output: JSON PipelineMessage objects
    
    Events:
        - PART: Streaming chunks (preview)
        - PREVIEW_TONE: Tone-adjusted preview chunks
        - END_TONE: Final cleaned, formatted, tone-adjusted text
    """
    await websocket.accept()
    
    # Generate session ID
    session_id = f"utt_{uuid.uuid4().hex[:8]}"
    logger.info(f"[{session_id}] Client connected (tone_mode={tone_mode})")
    
    # Create orchestrator for this session
    orchestrator = UnifiedPipelineOrchestrator(tone_mode=tone_mode)
    orchestrators[session_id] = orchestrator
    
    # Create queues
    audio_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    
    # Start pipeline processing task
    pipeline_task = asyncio.create_task(
        orchestrator.process_full_pipeline(session_id, audio_queue, output_queue)
    )
    
    # Task to send outputs to client
    async def send_outputs():
        try:
            while True:
                msg = await output_queue.get()
                try:
                    if websocket.client_state.name == "CONNECTED":
                        # Convert to dict for JSON serialization
                        msg_dict = {
                            "id": msg.id,
                            "chunk_index": msg.chunk_index,
                            "text": msg.text,
                            "event": msg.event,
                            "is_final": msg.is_final,
                            "end_of_speech_time": msg.end_of_speech_time
                        }
                        
                        # Add latency information if available
                        latency_info = {}
                        if hasattr(msg, '_asr_latency_ms'):
                            latency_info['asr_latency_ms'] = round(msg._asr_latency_ms, 2)
                        if hasattr(msg, '_disfluency_latency_ms'):
                            latency_info['disfluency_latency_ms'] = round(msg._disfluency_latency_ms, 2)
                        if hasattr(msg, '_grammar_latency_ms'):
                            latency_info['grammar_latency_ms'] = round(msg._grammar_latency_ms, 2)
                        if hasattr(msg, '_tone_latency_ms'):
                            latency_info['tone_latency_ms'] = round(msg._tone_latency_ms, 2)
                        
                        if latency_info:
                            msg_dict['latency_breakdown'] = latency_info
                            # Calculate total latency if all stages are present
                            if all(k in latency_info for k in ['asr_latency_ms', 'disfluency_latency_ms', 'grammar_latency_ms', 'tone_latency_ms']):
                                msg_dict['total_pipeline_latency_ms'] = round(
                                    sum(latency_info.values()), 2
                                )
                        
                        await websocket.send_json(msg_dict)
                        logger.debug(f"[{session_id}] Sent: {msg.event} - '{msg.text[:50]}...'")
                    else:
                        break
                except Exception as send_err:
                    logger.error(f"Error sending message: {send_err}")
                    break
                
                # If END_TONE, we're done
                if msg.event == "END_TONE":
                    logger.info(f"[{session_id}] Final output sent, closing connection")
                    break
        except Exception as e:
            logger.error(f"Error in output sender: {e}")
    
    sender_task = asyncio.create_task(send_outputs())
    
    try:
        # Receive audio chunks from client
        while True:
            try:
                data = await websocket.receive_bytes()
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                
                # Put in audio queue
                await audio_queue.put(audio_chunk)
                
            except WebSocketDisconnect:
                logger.info(f"[{session_id}] Client disconnected")
                break
            except Exception as e:
                logger.error(f"[{session_id}] Error receiving audio: {e}")
                break
                
    except Exception as e:
        logger.error(f"[{session_id}] WebSocket error: {e}")
    finally:
        # Signal end of audio stream
        await audio_queue.put(None)
        
        # Wait for tasks to complete with longer timeout
        try:
            # Give pipeline more time to complete (30 seconds)
            await asyncio.wait_for(pipeline_task, timeout=30.0)
            await asyncio.wait_for(sender_task, timeout=30.0)
        except asyncio.TimeoutError:
            logger.warning(f"[{session_id}] Tasks timed out, cancelling")
            pipeline_task.cancel()
            sender_task.cancel()
            # Try to send a final END_TONE message if pipeline didn't complete
            try:
                fallback_msg = {
                    "id": session_id,
                    "chunk_index": 0,
                    "text": "",
                    "event": "END_TONE",
                    "is_final": True,
                    "end_of_speech_time": None
                }
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_json(fallback_msg)
            except:
                pass
        
        # Cleanup
        orchestrators.pop(session_id, None)
        logger.info(f"[{session_id}] Session cleaned up")


@app.get("/")
async def root():
    """Serve the test UI"""
    ui_path = static_dir / "index.html"
    if ui_path.exists():
        return FileResponse(ui_path)
    return {"message": "UI not found. Please check static/index.html"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "unified_pipeline",
        "endpoints": {
            "ui": "/",
            "websocket": "/pipeline/stream?tone_mode={neutral|formal|casual|concise}",
            "docs": "/docs"
        }
    }


@app.get("/info")
async def info():
    """Pipeline information"""
    return {
        "name": "Unified Speech Dictation Pipeline",
        "stages": [
            "ASR (Speech-to-Text)",
            "Disfluency Removal (Fillers + Repetitions)",
            "Grammar Correction (MiniLM Transformer)",
            "Tone Transformation (Formal/Casual/Concise/Neutral)"
        ],
        "latency_target_ms": 1500,
        "features": [
            "Real-time streaming",
            "Low-latency processing",
            "Filler word removal",
            "Repetition detection",
            "Grammar correction",
            "Tone/style control",
            "Ready-to-use output"
        ],
        "tone_modes": ["neutral", "formal", "casual", "concise"]
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )

