#!/usr/bin/env python3
"""
Direct test of grammar engine without server
"""
import sys
sys.path.insert(0, 'src')

from grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage

print("=" * 70)
print("TESTING GRAMMAR ENGINE (MiniLM)")
print("=" * 70)

# Initialize engine
print("\nInitializing engine...")
engine = GrammarFormattingEngine()

# Test cases
test_cases = [
    "i think i really dont knows what to do",
    "he go to the store yesterday",
    "they was running in the park",
    "She have went to the market"
]

print("\n" + "=" * 70)

for i, text in enumerate(test_cases, 1):
    msg = PipelineMessage(
        id=f"test_{i:03d}",
        chunk_index=0,
        text=text,
        event="PART",
        is_final=False
    )
    
    print(f"\n[Test {i}]")
    print(f"  Input:  {text}")
    
    result = engine.process_message(msg)
    
    print(f"  Output: {result.text}")
    print(f"  Event:  {result.event}")

print("\n" + "=" * 70)
print("✅ All tests completed!")
print("=" * 70)
