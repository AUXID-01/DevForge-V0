# Unified Speech Dictation Pipeline

Complete streaming pipeline that connects all stages:
**ASR → Disfluency → Grammar → Tone**

## Architecture

```
Audio Input (WebSocket)
    ↓
ASR (Speech-to-Text)
    ↓
Disfluency Removal (Fillers + Repetitions)
    ↓
Grammar Correction (MiniLM Transformer)
    ↓
Tone Transformation (Formal/Casual/Concise/Neutral)
    ↓
Final Output (Ready-to-use text)
```

## Features

- ✅ Real-time streaming processing
- ✅ Low-latency (<1.5s target)
- ✅ Filler word removal
- ✅ Repetition detection
- ✅ Grammar correction (transformer-based)
- ✅ Tone/style control
- ✅ Ready-to-use output (no manual editing needed)

## Installation

### Quick Install (Recommended)

**Windows (PowerShell):**
```powershell
cd unified_pipeline
.\install_dependencies.ps1
```

**Linux/Mac:**
```bash
cd unified_pipeline
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Manual Install

1. Install unified pipeline dependencies:
```bash
cd unified_pipeline
pip install -r requirements.txt
```

2. Install spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

3. Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
```

4. Install component dependencies (optional, for full functionality):
```bash
# ASR-Audio
pip install -r ../ASR-Audio/requirements.txt

# Speech-dictation-engine (Grammar)
pip install -r ../speech-dictation-engine/requirements.txt

# ToneAndOrchestration
pip install -r ../toneAndOrchestration/requirements.txt
```

### PyTorch Installation (Windows)

If you encounter PyTorch installation issues on Windows:

**CPU version (recommended for testing):**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**CUDA version (if you have NVIDIA GPU):**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Component Modules

Ensure all component modules are available:
   - `ASR-Audio/` - ASR module
   - `DEvf/disfluency_module/` - Disfluency removal
   - `speech-dictation-engine/src/` - Grammar correction
   - `toneAndOrchestration/` - Tone transformation

## Usage

### Start the Server

```bash
python main.py
```

Server will start on `http://localhost:8003`

### WebSocket Endpoint

**Endpoint:** `ws://localhost:8003/pipeline/stream?tone_mode={mode}`

**Query Parameters:**
- `tone_mode`: One of `neutral`, `formal`, `casual`, `concise` (default: `neutral`)

**Input:**
- Audio chunks as bytes (float32 numpy array, 16kHz sample rate)

**Output:**
- JSON PipelineMessage objects with events:
  - `PART`: Streaming preview chunks
  - `PREVIEW_TONE`: Tone-adjusted preview chunks
  - `END_TONE`: Final cleaned, formatted, tone-adjusted text

### Example Client Code

```python
import asyncio
import websockets
import numpy as np
import json

async def test_pipeline():
    uri = "ws://localhost:8003/pipeline/stream?tone_mode=formal"
    
    async with websockets.connect(uri) as websocket:
        # Send audio chunks (example)
        audio_chunk = np.random.randn(1600).astype(np.float32)  # 0.1s at 16kHz
        await websocket.send(audio_chunk.tobytes())
        
        # Receive responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Event: {data['event']}, Text: {data['text']}")
            
            if data['event'] == 'END_TONE':
                print(f"\nFinal Output: {data['text']}")
                break

asyncio.run(test_pipeline())
```

## API Endpoints

### Health Check
```
GET /health
```

### Pipeline Info
```
GET /info
```

## Pipeline Stages

### 1. ASR (Speech-to-Text)
- Uses Whisper-based ASR engine
- Outputs: `PART` events with transcripts, `END_ASR` on completion

### 2. Disfluency Removal
- Removes filler words ("um", "uh", "like", etc.)
- Detects and removes repetitions
- Outputs: `PART` events with cleaned text, `END_CLEAN` on completion

### 3. Grammar Correction
- Uses MiniLM transformer for grammar correction
- Fixes subject-verb agreement, tense consistency, etc.
- Adds punctuation and capitalization
- Outputs: `PART` events with corrected text, `END_GRAMMAR` on completion

### 4. Tone Transformation
- Applies tone/style transformation (formal/casual/concise/neutral)
- Final formatting and cleanup
- Outputs: `PREVIEW_TONE` for chunks, `END_TONE` for final output

## Latency

The pipeline is designed to process streaming chunks with minimal latency:
- Each stage processes chunks as they arrive
- Total latency target: <1500ms after speech pause
- Latency is tracked via `end_of_speech_time` in messages

## Development

### Project Structure

```
unified_pipeline/
├── main.py                    # FastAPI server
├── pipeline_orchestrator.py   # Pipeline orchestration logic
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

### Testing

Test the pipeline with a simple client or use the WebSocket endpoint directly.

## Notes

- All processing happens in-memory for low latency
- Each session maintains its own state
- Components are shared across sessions for efficiency
- The pipeline handles errors gracefully and continues processing

