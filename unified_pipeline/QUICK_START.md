# Quick Start Guide - Unified Pipeline

## Prerequisites

1. All component modules must be available:
   - `ASR-Audio/` - ASR module with Whisper
   - `DEvf/disfluency_module/` - Disfluency removal
   - `speech-dictation-engine/src/` - Grammar correction
   - `toneAndOrchestration/` - Tone transformation

2. Install dependencies:

**Quick Install (Windows PowerShell):**
```powershell
cd unified_pipeline
.\install_dependencies.ps1
```

**Or Manual Install:**
```bash
cd unified_pipeline
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

## Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8003`

## Testing

### Option 1: Test with Mock Audio

```bash
python test_client.py --tone-mode formal --mock
```

### Option 2: Test with Real Microphone

```bash
python test_client.py --tone-mode formal
```

### Option 3: Use WebSocket Client

Connect to: `ws://localhost:8003/pipeline/stream?tone_mode=formal`

Send audio chunks as bytes (float32 numpy array, 16kHz sample rate).

## Pipeline Flow

1. **Audio Input** → WebSocket receives audio chunks
2. **ASR** → Converts speech to text (PART events)
3. **Disfluency** → Removes fillers and repetitions (PART events)
4. **Grammar** → Corrects grammar and formats (PART events)
5. **Tone** → Applies tone transformation (PREVIEW_TONE, then END_TONE)

## Output Events

- `PART`: Streaming text chunks (preview)
- `PREVIEW_TONE`: Tone-adjusted preview chunks
- `END_TONE`: Final ready-to-use text

## Example Response

```json
{
  "id": "utt_abc123",
  "chunk_index": 0,
  "text": "I think we should proceed with the plan.",
  "event": "END_TONE",
  "is_final": true,
  "end_of_speech_time": 1234.5
}
```

## Troubleshooting

### Connection Refused
- Make sure the server is running: `python main.py`
- Check if port 8003 is available

### Import Errors
- Ensure all component modules are in the parent directory
- Check Python path includes all necessary directories

### No Output
- Check server logs for errors
- Verify audio format (float32, 16kHz)
- Ensure ASR model is loaded correctly

## Next Steps

For production use:
1. Add authentication/authorization
2. Add rate limiting
3. Add monitoring and logging
4. Optimize for your specific latency requirements

