#!/usr/bin/env python3
"""
Quick test script for the Grammar API
"""
import requests
import json

# Test data
test_cases = [
    {
        "id": "test_001",
        "chunk_index": 0,
        "text": "i think i really dont knows what to do",
        "event": "PART",
        "is_final": False
    },
    {
        "id": "test_002",
        "chunk_index": 0,
        "text": "he go to the store yesterday",
        "event": "PART",
        "is_final": False
    },
    {
        "id": "test_003",
        "chunk_index": 0,
        "text": "they was running in the park",
        "event": "PART",
        "is_final": False
    }
]

print("=" * 70)
print("TESTING GRAMMAR & FORMATTING API")
print("=" * 70)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n[Test {i}]")
    print(f"Input:  {test_case['text']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/process",
            json=test_case,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Output: {result['text']}")
            print(f"Event:  {result['event']}")
        else:
            print(f"Error: Status {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("Make sure server is running: uvicorn src.grammar_unified_pipeline_minilm:app --port 8000")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
