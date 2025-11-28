# Grammar Stage Integration Guide

## Overview
This is the **Grammar & Formatting Stage (Person C)** in the speech dictation pipeline.

**Your Role:** Receive cleaned text from the filler removal stage → Correct grammar → Send to tone stage

---

## Quick Start

### 1. Start the Server
```bash
cd /home/vedu/Work/speech-dictation-engine
source activate.sh  # or: venv/bin/activate
python run.py start
```

Server will be available at: `http://localhost:8000`

### 2. API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Process Message
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "utterance_001",
    "chunk_index": 0,
    "text": "he go to the store yesterday",
    "event": "PART",
    "is_final": false
  }'
```

---

## Message Schema (PipelineMessage)

### Input from Person B (Filler Removal)
```json
{
  "id": "utterance_001",              // Unique utterance ID
  "chunk_index": 0,                   // Sequential chunk number
  "text": "he go to the store",       // Cleaned text (no fillers)
  "event": "PART",                    // "PART" or "END_CLEAN"
  "is_final": false,                  // Stable/final from ASR
  "end_of_speech_time": 1250.5        // ms since start (optional)
}
```

### Output to Person D (Tone Stage)
```json
{
  "id": "utterance_001",
  "chunk_index": 0,
  "text": "He went to the store.",    // Grammar corrected + formatted
  "event": "PART",                    // "PART" or "END_GRAMMAR"
  "is_final": false,
  "end_of_speech_time": 1250.5        // Passed through
}
```

---

## Integration Methods

### Method 1: HTTP REST API (Recommended)

**From Person B to You:**
```python
import requests

# Person B sends to your grammar stage
response = requests.post(
    "http://localhost:8000/process",
    json={
        "id": "utt_001",
        "chunk_index": 0,
        "text": "he go to the store",
        "event": "PART",
        "is_final": False
    }
)

result = response.json()
# Send result to Person D (tone stage)
```

**You to Person D:**
```python
# Forward corrected message to tone stage
tone_response = requests.post(
    "http://tone-stage-url:8001/process",  # Person D's endpoint
    json=result
)
```

### Method 2: Direct Python Integration

```python
from src.grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage

# Initialize once at startup
grammar_engine = GrammarFormattingEngine()

# Process message
input_msg = PipelineMessage(
    id="utt_001",
    chunk_index=0,
    text="he go to the store",
    event="PART",
    is_final=False
)

output_msg = grammar_engine.process_message(input_msg)
print(output_msg.text)  # "He went to the store."
```

### Method 3: Message Queue (RabbitMQ/Kafka)

```python
import pika
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='queue_b_to_c')  # Input from Person B
channel.queue_declare(queue='queue_c_to_d')  # Output to Person D

# Initialize engine
grammar_engine = GrammarFormattingEngine()

def callback(ch, method, properties, body):
    # Receive from Person B
    msg_dict = json.loads(body)
    input_msg = PipelineMessage(**msg_dict)
    
    # Process
    output_msg = grammar_engine.process_message(input_msg)
    
    # Send to Person D
    channel.basic_publish(
        exchange='',
        routing_key='queue_c_to_d',
        body=json.dumps(output_msg.dict())
    )
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming
channel.basic_consume(queue='queue_b_to_c', on_message_callback=callback)
channel.start_consuming()
```

---

## Event Flow

### Regular Chunks
```
Person B → "PART" → Your Grammar Stage → "PART" → Person D
```

### End of Utterance
```
Person B → "END_CLEAN" → Your Grammar Stage → "END_GRAMMAR" → Person D
```

---

## Performance

- **Initialization:** ~2.7 seconds (one-time at startup)
- **First request:** ~700ms (warmup)
- **Sustained:** ~120ms average per chunk
- **P95:** ~125ms

---

## Error Handling

The engine automatically:
- Falls back to rule-based correction if model fails
- Preserves original text if processing fails
- Logs all errors for debugging

---

## Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model (if not done)
python -m spacy download en_core_web_sm

# The T5 model (~892MB) downloads automatically on first run
```

---

## Testing

```bash
# Test grammar correction directly
venv/bin/python test_grammar.py

# Test latency
venv/bin/python test_latency.py

# Test API (start server first)
venv/bin/python test_api.py
```

---

## Configuration

Edit `src/config.py` for customization:
- Model name
- Max chunk size
- Timeouts
- Logging levels

---

## Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY src/ ./src/
COPY run.py .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.grammar_unified_pipeline_minilm:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t grammar-stage .
docker run -p 8000:8000 grammar-stage
```

---

## Contact Points

**Receive from:** Person B (Filler Removal Stage)
- Endpoint: You expose `/process`
- They POST to your endpoint

**Send to:** Person D (Tone Stage)
- Endpoint: They expose their endpoint
- You POST to their endpoint

---

## Troubleshooting

### Model not loading
- Check `torch` installation: `pip install torch>=2.0.0`
- Check model: `vennify/t5-base-grammar-correction`

### Port already in use
- Change port: `uvicorn ... --port 8001`
- Or kill existing: `pkill -f uvicorn`

### High latency
- First request is always slow (warmup)
- Use GPU if available
- Consider batch processing for multiple chunks

---

## Next Steps for Integration

1. **Coordinate with Person B:**
   - Get their endpoint URL
   - Agree on message format
   - Test connection

2. **Coordinate with Person D:**
   - Share your endpoint: `http://your-host:8000/process`
   - Get their endpoint for forwarding
   - Test end-to-end flow

3. **Set up monitoring:**
   - Log all requests/responses
   - Track latency metrics
   - Alert on failures

4. **Load testing:**
   - Test with realistic traffic
   - Verify sustained performance
   - Check memory usage

---

## Ready to Integrate! 🚀

Your grammar stage is production-ready. Share this guide with your team members.
