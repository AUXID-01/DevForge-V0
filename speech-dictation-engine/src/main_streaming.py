"""
Grammar & Formatting Engine - FastAPI Streaming Endpoints

Provides two integration patterns:
1. Per-chunk HTTP endpoint (simple, easy to integrate)
2. WebSocket streaming (for real-time, low-latency)
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import Dict, Optional

from src.grammar_formatter_streaming import (
    GrammarFormattingStreamingEngine,
    ChunkMessageIn,
    GrammarFormattingSyncWorker
)
import queue

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grammar & Formatting Engine (Streaming)",
    description="Classical NLP stage in speech dictation pipeline",
    version="2.0.0"
)

# CORS for team integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance (loaded once at startup)
grammar_engine: Optional[GrammarFormattingStreamingEngine] = None


# ========== REQUEST/RESPONSE MODELS ==========

class GrammarChunkRequest(BaseModel):
    """Request to process a single chunk"""
    id: str                      # Utterance ID
    cleaned_text: str            # Text from filler/repetition stage
    chunk_index: int             # For ordering
    context_hint: Optional[str] = None  # Previous sentence (optional)
    end_of_speech: bool = False  # Is this the final chunk?
    
    class Config:
        example = {
            "id": "utt_12345",
            "cleaned_text": "he go to the store",
            "chunk_index": 0,
            "context_hint": None,
            "end_of_speech": False
        }


class GrammarChunkResponse(BaseModel):
    """Response with formatted chunk"""
    id: str
    formatted_text: str          # Grammar-corrected output
    chunk_index: int
    end_of_speech: bool
    latency_ms: float            # Processing time
    
    class Config:
        example = {
            "id": "utt_12345",
            "formatted_text": "He went to the store.",
            "chunk_index": 0,
            "end_of_speech": False,
            "latency_ms": 45.2
        }


# ========== STARTUP/SHUTDOWN ==========

@app.on_event("startup")
async def startup():
    """Initialize engine at server startup"""
    global grammar_engine
    logger.info("🚀 Initializing Grammar Engine...")
    grammar_engine = GrammarFormattingStreamingEngine()
    logger.info("✅ Engine ready")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup at shutdown"""
    logger.info("Shutting down Grammar Engine")


# ========== SIMPLE PER-CHUNK ENDPOINT (PATTERN 1) ==========

@app.post("/process/chunk", response_model=GrammarChunkResponse)
async def process_chunk(request: GrammarChunkRequest):
    """
    Process a single chunk.
    
    This is the simplest integration: other team members call this endpoint
    for each chunk from their filler/repetition stage.
    
    Usage:
    ```
    POST /process/chunk
    {
      "id": "utt_001",
      "cleaned_text": "he go to the store",
      "chunk_index": 0,
      "end_of_speech": false
    }
    ```
    
    Response:
    ```
    {
      "id": "utt_001",
      "formatted_text": "He went to the store.",
      "chunk_index": 0,
      "end_of_speech": false,
      "latency_ms": 45.2
    }
    ```
    """
    
    if grammar_engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        # Create input message
        msg_in = ChunkMessageIn(
            id=request.id,
            cleaned_text=request.cleaned_text,
            chunk_index=request.chunk_index,
            context_hint=request.context_hint,
            end_of_speech=request.end_of_speech
        )
        
        # Process
        msg_out = grammar_engine.process_chunk(msg_in)
        
        return GrammarChunkResponse(
            id=msg_out.id,
            formatted_text=msg_out.formatted_text,
            chunk_index=msg_out.chunk_index,
            end_of_speech=msg_out.end_of_speech,
            latency_ms=0.0  # Measured internally
        )
    
    except Exception as e:
        logger.error(f"Error processing chunk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== WEBSOCKET STREAMING ENDPOINT (PATTERN 2) ==========

@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming.
    
    This allows continuous streaming without per-request overhead.
    
    Protocol:
    1. Client connects
    2. Client sends JSON messages with chunk data
    3. Server processes and sends back formatted chunks in real-time
    4. Client sends {"_type": "END"} to close
    
    Usage (Python):
    ```
    import asyncio
    import websockets
    import json
    
    async def test():
        uri = "ws://localhost:8000/stream"
        async with websockets.connect(uri) as websocket:
            # Send chunk 1
            await websocket.send(json.dumps({
                "id": "utt_001",
                "cleaned_text": "he go to store",
                "chunk_index": 0,
                "end_of_speech": False
            }))
            response = await websocket.recv()
            print(json.loads(response))
            
            # Send chunk 2
            await websocket.send(json.dumps({
                "id": "utt_001",
                "cleaned_text": "and buy milk",
                "chunk_index": 1,
                "end_of_speech": True
            }))
            response = await websocket.recv()
            print(json.loads(response))
    
    asyncio.run(test())
    ```
    """
    
    await websocket.accept()
    logger.info(f"WebSocket client connected")
    
    try:
        while True:
            # Receive chunk from client
            data = await websocket.receive_text()
            msg_dict = json.loads(data)
            
            # Check for END signal
            if msg_dict.get("_type") == "END":
                logger.info("WebSocket client sent END signal")
                await websocket.send_json({"_type": "END"})
                break
            
            try:
                # Process chunk
                msg_in = ChunkMessageIn(
                    id=msg_dict['id'],
                    cleaned_text=msg_dict['cleaned_text'],
                    chunk_index=msg_dict['chunk_index'],
                    context_hint=msg_dict.get('context_hint'),
                    end_of_speech=msg_dict.get('end_of_speech', False)
                )
                
                msg_out = grammar_engine.process_chunk(msg_in)
                
                # Send formatted chunk back
                response = {
                    'id': msg_out.id,
                    'formatted_text': msg_out.formatted_text,
                    'chunk_index': msg_out.chunk_index,
                    'end_of_speech': msg_out.end_of_speech
                }
                
                await websocket.send_json(response)
            
            except Exception as e:
                logger.error(f"Error processing WebSocket chunk: {e}")
                await websocket.send_json({
                    "_type": "ERROR",
                    "message": str(e)
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        await websocket.close()
        logger.info("WebSocket client disconnected")


# ========== BATCH ENDPOINT (for testing/debugging) ==========

class GrammarBatchRequest(BaseModel):
    """Process multiple chunks at once"""
    id: str
    chunks: list[Dict]  # List of {cleaned_text, chunk_index, is_final}


class GrammarBatchResponse(BaseModel):
    """Response with all formatted chunks"""
    id: str
    formatted_chunks: list[Dict]  # List of {formatted_text, chunk_index}


@app.post("/process/batch", response_model=GrammarBatchResponse)
async def process_batch(request: GrammarBatchRequest):
    """
    Process multiple chunks for testing purposes.
    
    NOT recommended for production (use streaming instead).
    """
    
    if grammar_engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        formatted_chunks = []
        
        for chunk_data in request.chunks:
            msg_in = ChunkMessageIn(
                id=request.id,
                cleaned_text=chunk_data['cleaned_text'],
                chunk_index=chunk_data['chunk_index'],
                context_hint=chunk_data.get('context_hint'),
                end_of_speech=chunk_data.get('is_final', False)
            )
            
            msg_out = grammar_engine.process_chunk(msg_in)
            formatted_chunks.append({
                'formatted_text': msg_out.formatted_text,
                'chunk_index': msg_out.chunk_index
            })
        
        return GrammarBatchResponse(
            id=request.id,
            formatted_chunks=formatted_chunks
        )
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== HEALTH & INFO ENDPOINTS ==========

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "engine": "streaming_classical_npl",
        "version": "2.0.0",
        "context_mode": "per_id_state"
    }


@app.get("/info")
async def info():
    """API information"""
    return {
        "name": "Grammar & Formatting Engine",
        "role": "Queue B → Queue C Worker",
        "version": "2.0.0",
        "patterns": [
            {
                "name": "Per-Chunk HTTP",
                "endpoint": "POST /process/chunk",
                "use": "Simple, request-response for each chunk"
            },
            {
                "name": "WebSocket Streaming",
                "endpoint": "WS /stream",
                "use": "Real-time streaming, low latency"
            },
            {
                "name": "Batch Processing",
                "endpoint": "POST /process/batch",
                "use": "Testing/debugging only"
            }
        ],
        "message_schema": {
            "input": {
                "id": "str (utterance ID)",
                "cleaned_text": "str (from filler stage)",
                "chunk_index": "int (for ordering)",
                "context_hint": "Optional[str] (previous sentence)",
                "end_of_speech": "bool (final chunk?)"
            },
            "output": {
                "id": "str",
                "formatted_text": "str (grammar-corrected)",
                "chunk_index": "int",
                "end_of_speech": "bool"
            }
        }
    }


@app.get("/docs")
async def docs_redirect():
    """Redirect to API documentation"""
    return {"message": "See /docs for interactive documentation"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
