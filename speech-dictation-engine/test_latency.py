#!/usr/bin/env python3
"""
Latency test for grammar engine
Measures processing time for various input lengths
"""
import sys
import time
sys.path.insert(0, 'src')

from grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage

print("=" * 70)
print("GRAMMAR ENGINE LATENCY TEST")
print("=" * 70)

# Initialize engine
print("\nInitializing engine...")
start_init = time.time()
engine = GrammarFormattingEngine()
init_time = (time.time() - start_init) * 1000
print(f"✅ Engine initialized in {init_time:.1f}ms")

# Test cases with different lengths
test_cases = [
    {
        "name": "Short (8 words)",
        "text": "i think i really dont knows what to do"
    },
    {
        "name": "Medium (15 words)",
        "text": "he go to the store yesterday and buy some milk and bread for the family"
    },
    {
        "name": "Long (25 words)",
        "text": "they was running in the park when it start to rain so they decide to go home but forgot their umbrella at the bench"
    },
    {
        "name": "Very Short (3 words)",
        "text": "he go store"
    }
]

print("\n" + "=" * 70)
print("LATENCY MEASUREMENTS (3 runs each)")
print("=" * 70)

for test in test_cases:
    print(f"\n[{test['name']}]")
    print(f"Input: {test['text']}")
    
    latencies = []
    output = None
    
    # Run 3 times to get average
    for run in range(3):
        msg = PipelineMessage(
            id=f"latency_test",
            chunk_index=0,
            text=test['text'],
            event="PART",
            is_final=False
        )
        
        start = time.time()
        result = engine.process_message(msg)
        latency = (time.time() - start) * 1000
        
        latencies.append(latency)
        if run == 0:
            output = result.text
    
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    
    print(f"Output: {output}")
    print(f"Latency:")
    print(f"  - Min: {min_latency:.1f}ms")
    print(f"  - Max: {max_latency:.1f}ms")
    print(f"  - Avg: {avg_latency:.1f}ms")
    print(f"  - Run 1: {latencies[0]:.1f}ms")
    print(f"  - Run 2: {latencies[1]:.1f}ms")
    print(f"  - Run 3: {latencies[2]:.1f}ms")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Test sustained load
print("\nSustained Load Test (10 requests)...")
sustained_latencies = []
test_text = "he go to the store yesterday"

for i in range(10):
    msg = PipelineMessage(
        id=f"load_test_{i}",
        chunk_index=0,
        text=test_text,
        event="PART",
        is_final=False
    )
    
    start = time.time()
    result = engine.process_message(msg)
    latency = (time.time() - start) * 1000
    sustained_latencies.append(latency)

avg_sustained = sum(sustained_latencies) / len(sustained_latencies)
print(f"\nSustained Average: {avg_sustained:.1f}ms")
print(f"P50 (median): {sorted(sustained_latencies)[5]:.1f}ms")
print(f"P95: {sorted(sustained_latencies)[9]:.1f}ms")

print("\n" + "=" * 70)
print("✅ Latency test completed!")
print("=" * 70)
