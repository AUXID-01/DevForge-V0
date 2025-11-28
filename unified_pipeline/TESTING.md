# Testing Guide - Unified Pipeline

## Option 1: Web UI (Easiest)

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Open your browser:**
   Navigate to: `http://localhost:8003/`

3. **Use the UI:**
   - Select tone mode (neutral/formal/casual/concise)
   - Click "Connect"
   - Click "Start Recording"
   - Speak into your microphone
   - Watch the pipeline output in real-time!

## Option 2: Test Client Script

### With Mock Audio (No Microphone Needed)

```bash
python test_client.py --tone-mode formal --mock
```

This sends mock audio data to test the pipeline without needing a microphone.

### With Real Microphone

```bash
python test_client.py --tone-mode formal
```

This uses your system's microphone to capture real audio.

## Option 3: WebSocket Client (Programmatic)

### Python Example

```python
import asyncio
import websockets
import numpy as np
import json

async def test_pipeline():
    uri = "ws://localhost:8003/pipeline/stream?tone_mode=formal"
    
    async with websockets.connect(uri) as websocket:
        # Send audio chunks (example: mock audio)
        for i in range(10):
            audio_chunk = np.random.randn(1600).astype(np.float32) * 0.1
            await websocket.send(audio_chunk.tobytes())
            await asyncio.sleep(0.1)
        
        # Receive responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Event: {data['event']}, Text: {data['text']}")
            
            if data['event'] == 'END_TONE':
                print(f"\n✅ Final Output: {data['text']}")
                break

asyncio.run(test_pipeline())
```

### JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8003/pipeline/stream?tone_mode=formal');

ws.onopen = () => {
    console.log('Connected');
    // Send audio chunks (Float32Array)
    // ws.send(audioBuffer);
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data.event, 'Text:', data.text);
    
    if (data.event === 'END_TONE') {
        console.log('Final output:', data.text);
    }
};
```

## Option 4: Using curl/HTTP (Health Check Only)

```bash
# Check if server is running
curl http://localhost:8003/health

# View API documentation
# Open http://localhost:8003/docs in browser
```

## Expected Output Events

1. **PART** - Raw streaming chunks from ASR
2. **PREVIEW_TONE** - Tone-adjusted preview chunks
3. **END_TONE** - Final cleaned, formatted, tone-adjusted text

## Troubleshooting

### Microphone Not Working
- Check browser permissions (for web UI)
- Ensure microphone is connected and working
- Try the mock audio test first

### Connection Refused
- Make sure server is running: `python main.py`
- Check if port 8003 is available
- Try `http://localhost:8003/health` to verify

### No Output
- Check server logs for errors
- Verify audio format (16kHz, float32)
- Ensure all dependencies are installed

### Browser Compatibility
- Use Chrome, Firefox, or Edge (latest versions)
- HTTPS may be required for microphone access (use localhost which is exempt)

## Testing Different Tone Modes

Test all four tone modes to see the differences:

- **Neutral**: No transformation
- **Formal**: Expands contractions, removes casual words
- **Casual**: Simplifies formal language
- **Concise**: Removes hedging phrases and intensifiers

## Performance Testing

Monitor latency in the UI or check the `end_of_speech_time` in responses. Target is <1500ms total latency.

