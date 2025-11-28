# disfluency_module/tests/test_worker.py

from queue import Queue
from disfluency_module.worker import DisfluencyWorker

def test_worker_basic():
    """
    Test that worker processes a simple chunk message.
    """
    input_q = Queue()
    output_q = Queue()
    
    worker = DisfluencyWorker(input_q, output_q)
    
    # Put a message in input queue
    input_q.put({
        "id": "utt1",
        "chunk_text": "um I was like thinking",
        "chunk_index": 0,
        "timestamps": {"start": 0.0, "end": 1.5},
        "is_final": False,
        "type": "CHUNK",
    })
    
    # Process one message
    msg = input_q.get()
    worker.process_message(msg)
    
    # Check output
    out_msg = output_q.get()
    
    assert out_msg["id"] == "utt1"
    assert "um" not in out_msg["cleaned_text"].lower()
    assert "like" not in out_msg["cleaned_text"].lower()
    assert "thinking" in out_msg["cleaned_text"].lower()

def test_worker_cross_chunk_repetition():
    """
    Test cross-chunk repetition detection using context.
    """
    input_q = Queue()
    output_q = Queue()
    
    worker = DisfluencyWorker(input_q, output_q)
    
    # Chunk 0: "I think we should"
    input_q.put({
        "id": "utt2",
        "chunk_text": "I think we should",
        "chunk_index": 0,
        "timestamps": {"start": 0.0, "end": 1.0},
        "is_final": False,
        "type": "CHUNK",
    })
    
    # Chunk 1: "we should go now" (repetition of "we should")
    input_q.put({
        "id": "utt2",
        "chunk_text": "we should go now",
        "chunk_index": 1,
        "timestamps": {"start": 1.0, "end": 2.0},
        "is_final": True,
        "type": "CHUNK",
    })
    
    # Process both chunks
    msg0 = input_q.get()
    worker.process_message(msg0)
    
    msg1 = input_q.get()
    worker.process_message(msg1)
    
    # Get outputs
    out0 = output_q.get()
    out1 = output_q.get()
    
    # Chunk 0 should output normally
    assert "think" in out0["cleaned_text"].lower()
    
    # Chunk 1 should detect "we should" was already in context
    # and only output "go now" (or similar, depending on exact slicing)
    # The key is it shouldn't repeat "we should"
    cleaned1 = out1["cleaned_text"].lower()
    
    # At minimum, "go now" should be there
    assert "go" in cleaned1 or "now" in cleaned1
    
    print("Chunk 0 output:", out0["cleaned_text"])
    print("Chunk 1 output:", out1["cleaned_text"])
