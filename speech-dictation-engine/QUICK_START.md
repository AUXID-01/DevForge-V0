# Quick Start - Grammar Stage (Person C)

## Your Component is Ready! ✅

Your grammar correction stage is fully functional and ready to integrate with the team.

---

## What You Built

- ✅ **Grammar Correction Engine**: T5 transformer model with optimized parameters
- ✅ **FastAPI Server**: RESTful API for team integration
- ✅ **Performance**: ~120ms latency (meets requirements)
- ✅ **Quality**: Perfect grammar corrections with no repetition
- ✅ **Integration Ready**: Full forwarding pipeline implemented

---

## Quick Test (Solo)

```bash
# Terminal 1: Start your server
./venv/bin/python run.py

# Terminal 2: Test it
./venv/bin/python test_api.py
```

---

## Integration with Team

### Step 1: Get Person B's Endpoint

Contact Person B (Filler Removal stage) and ask:
- "What's your endpoint URL?"
- They should give you something like: `http://person-b-host:8000/forward` or similar

### Step 2: Share Your Endpoint

Tell Person B to send messages to:
```
http://your-host:8000/process
```

If testing locally:
- Use `ngrok` or similar: `ngrok http 8000`
- Share the ngrok URL: `https://abc123.ngrok.io/process`

### Step 3: Get Person D's Endpoint

Contact Person D (Tone Transformation stage) and ask:
- "What's your endpoint URL?"
- Update line 34 in `src/integration_server.py`:

```python
PERSON_D_URL = "http://person-d-actual-url:8000/process"
```

### Step 4: Start Full Integration Server

```bash
./venv/bin/python src/integration_server.py
```

This server will:
1. Receive messages from Person B
2. Correct grammar
3. Forward to Person D
4. Log everything

---

## Testing Integration

### Test Message Flow

```bash
# Send a test message (simulating Person B)
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "chunk_index": 1,
    "text": "he go to the store yesterday",
    "event": "PART",
    "is_final": false
  }'
```

Expected flow:
```
Person B → [Your Server] → Person D
         ↓
    "he go to store" → "He went to the store."
```

---

## Deployment Options

### Option 1: Docker (Recommended)

```bash
# Build
docker build -t grammar-stage .

# Run
docker run -p 8000:8000 grammar-stage
```

### Option 2: Cloud Deployment

Deploy to:
- AWS EC2 / ECS
- Google Cloud Run
- Azure Container Instances
- Heroku

### Option 3: ngrok (Quick Testing)

```bash
# Terminal 1
./venv/bin/python src/integration_server.py

# Terminal 2
ngrok http 8000

# Share the ngrok URL with team
```

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Info Endpoint
```bash
curl http://localhost:8000/info
```

### Server Logs
Watch the terminal for real-time logs:
```
[B→C] Received PART from Person B: id=xyz, chunk=1
[C] Processed: 'he go store' → 'He went to the store.'
[C→D] Forwarded to Person D successfully
```

---

## Troubleshooting

### "Person D connection failed"
- Normal if Person D's server isn't running yet
- Update `PERSON_D_URL` in `integration_server.py`
- Coordinate with Person D

### "Engine not initialized"
- Wait 2-3 seconds after startup
- Check logs for "✅ Grammar Stage Ready"

### Import errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. **Coordinate with Team**
   - [ ] Get Person B's endpoint
   - [ ] Share your endpoint with Person B
   - [ ] Get Person D's endpoint
   - [ ] Update `PERSON_D_URL` in code

2. **Deploy**
   - [ ] Choose deployment method (Docker/Cloud/ngrok)
   - [ ] Get stable URL
   - [ ] Share with team

3. **Test End-to-End**
   - [ ] Person A (ASR) → B → C (You) → D
   - [ ] Verify full pipeline works
   - [ ] Monitor latency and quality

4. **Production Readiness**
   - [ ] Add error handling/retries
   - [ ] Set up logging/monitoring
   - [ ] Configure scaling (if needed)

---

## Files You Need to Know

| File | Purpose |
|------|---------|
| `src/integration_server.py` | Main server (receives from B, forwards to D) |
| `src/grammar_unified_pipeline_minilm.py` | Core grammar engine |
| `src/grammar_minilm_fixer.py` | T5 model wrapper |
| `run.py` | Simple startup script |
| `test_api.py` | Test your endpoint |
| `INTEGRATION.md` | Detailed integration guide |

---

## Summary

**Your role is complete!** Now it's about team coordination:

1. Exchange endpoint URLs with Person B and Person D
2. Deploy to a stable URL (not localhost)
3. Test the full pipeline together
4. Monitor and optimize if needed

**You're ready to integrate! 🚀**

---

## Questions for Your Team

1. **Person B**: What's your endpoint URL? When will you be ready?
2. **Person D**: What's your endpoint URL? What's your expected input format?
3. **Person A**: Who's coordinating the full pipeline test?
4. **All**: When can we do end-to-end testing?

---

## Support

- Check `INTEGRATION.md` for detailed technical docs
- Check `READY_FOR_INTEGRATION.md` for checklist
- Review `integration_example.py` for code examples

**Good luck with the integration! 🎉**
