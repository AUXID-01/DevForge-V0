"""
Full Integration Server
Receives from Person B → Process → Forward to Person D
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
from src.grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grammar Stage (Person C)",
    description="Receives from filler stage, corrects grammar, forwards to tone stage",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine
grammar_engine = None

# Configure Person D's endpoint (TODO: Update this)
PERSON_D_URL = "http://localhost:8001/process"  # Person D's tone stage


@app.on_event("startup")
async def startup():
    """Initialize grammar engine at startup"""
    global grammar_engine
    logger.info("🚀 Initializing Grammar Stage...")
    grammar_engine = GrammarFormattingEngine()
    logger.info("✅ Grammar Stage Ready")


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "stage": "grammar_correction",
        "person": "C",
        "receives_from": "person_b_filler_removal",
        "forwards_to": "person_d_tone_transformation"
    }


@app.post("/process")
async def process_from_person_b(msg: PipelineMessage):
    """
    Main endpoint: Receive from Person B, process, forward to Person D
    
    This is what Person B will call to send you messages.
    """
    
    if grammar_engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        logger.info(f"[B→C] Received {msg.event} from Person B: id={msg.id}, chunk={msg.chunk_index}")
        
        # Process through grammar engine
        processed_msg = grammar_engine.process_message(msg)
        
        logger.info(f"[C] Processed: '{msg.text}' → '{processed_msg.text}'")
        
        # Forward to Person D (tone stage)
        try:
            response = requests.post(
                PERSON_D_URL,
                json=processed_msg.model_dump(),
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"[C→D] Forwarded to Person D successfully")
            else:
                logger.warning(f"[C→D] Person D returned {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"[C→D] Could not connect to Person D at {PERSON_D_URL}")
        except Exception as e:
            logger.error(f"[C→D] Error forwarding to Person D: {e}")
        
        # Return processed message (for debugging/monitoring)
        return processed_msg
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info")
async def info():
    """Integration information"""
    return {
        "stage": "Grammar & Formatting (Person C)",
        "role": "Correct grammar errors, format text",
        "input_from": "Person B (Filler Removal)",
        "output_to": "Person D (Tone Transformation)",
        "endpoints": {
            "receive": "POST /process",
            "health": "GET /health",
            "info": "GET /info"
        },
        "message_schema": {
            "id": "string (utterance ID)",
            "chunk_index": "integer (sequence number)",
            "text": "string (text to process)",
            "event": "string (PART, END_CLEAN, etc.)",
            "is_final": "boolean",
            "end_of_speech_time": "float (optional)"
        },
        "person_d_endpoint": PERSON_D_URL,
        "your_endpoint": "http://your-host:8000/process"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("GRAMMAR STAGE (PERSON C) - FULL INTEGRATION SERVER")
    print("=" * 70)
    print("\nStarting server...")
    print("Your endpoint: http://localhost:8000/process")
    print(f"Forwarding to Person D: {PERSON_D_URL}")
    print("\nPerson B should POST messages to: http://localhost:8000/process")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
