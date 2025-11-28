# scripts/run_full_pipeline.py
"""
Full Pipeline Demo - Uses Real Components

This script demonstrates the full pipeline using real components:
ASR → Disfluency → Grammar → Tone

For production use, use the unified_pipeline/main.py WebSocket server.
"""

import sys
import time
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ASR-Audio"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "DEvf"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "speech-dictation-engine" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "unified_pipeline"))

from mocks.mock_asr import mock_asr_stream
from orchestrator.orchestrator import PipelineOrchestrator
from schemas.pipeline_message import PipelineMessage
from unified_pipeline.pipeline_orchestrator import UnifiedPipelineOrchestrator


def main():
    print("=== Full Pipeline Demo (Real Components) ===")
    print("\nNote: For streaming WebSocket usage, use unified_pipeline/main.py")
    print()

    utt_id = "demo_utt"

    tone_mode = input("Enter tone mode (formal/casual/concise/neutral): ").strip().lower()
    if tone_mode not in {"formal", "casual", "concise", "neutral"}:
        print("Invalid mode, defaulting to neutral.")
        tone_mode = "neutral"

    print(f"\nUsing tone mode: {tone_mode}")
    print("=" * 60)

    # Option 1: Use UnifiedPipelineOrchestrator (recommended for async/streaming)
    # For this demo, we'll use the component-by-component approach
    
    # Initialize components
    from disfluency_module.worker import DisfluencyWorker
    from disfluency_module.schema import PipelineMessage as DisfluencyPipelineMessage
    from grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage as GrammarPipelineMessage
    
    grammar_engine = GrammarFormattingEngine()
    tone_orch = PipelineOrchestrator(tone_mode=tone_mode)
    
    # 1) ASR (using mock for demo, but structure is same)
    print("\n[1] ASR Stage")
    print("-" * 60)
    asr_msgs = mock_asr_stream(utt_id)
    eos_time = time.time()
    for m in asr_msgs:
        if m.event == "END_ASR":
            m.end_of_speech_time = eos_time
    
    for m in asr_msgs:
        if m.event == "PART":
            print(f"  ASR PART[{m.chunk_index}]: {m.text}")

    # 2) Disfluency Removal
    print("\n[2] Disfluency Removal Stage")
    print("-" * 60)
    disfluency_input = []
    disfluency_output = []
    disfluency_worker = DisfluencyWorker(disfluency_input, disfluency_output)
    
    clean_msgs = []
    for asr_msg in asr_msgs:
        # Convert to disfluency schema
        disfluency_msg = DisfluencyPipelineMessage(
            id=asr_msg.id,
            chunk_index=asr_msg.chunk_index,
            text=asr_msg.text,
            event=asr_msg.event,
            is_final=asr_msg.is_final,
            end_of_speech_time=asr_msg.end_of_speech_time
        )
        disfluency_worker.process_message(disfluency_msg)
        if disfluency_output:
            clean_msgs.append(disfluency_output.pop(0))
    
    for m in clean_msgs:
        if m.event == "PART":
            print(f"  CLEAN PART[{m.chunk_index}]: {m.text}")

    # 3) Grammar Correction
    print("\n[3] Grammar Correction Stage")
    print("-" * 60)
    grammar_msgs = []
    for clean_msg in clean_msgs:
        # Convert to grammar schema
        grammar_msg = GrammarPipelineMessage(
            id=clean_msg.id,
            chunk_index=clean_msg.chunk_index,
            text=clean_msg.text,
            event=clean_msg.event,
            is_final=clean_msg.is_final,
            end_of_speech_time=clean_msg.end_of_speech_time
        )
        result = grammar_engine.process_message(grammar_msg)
        grammar_msgs.append(result)
    
    for m in grammar_msgs:
        if m.event == "PART":
            print(f"  GRAMMAR PART[{m.chunk_index}]: {m.text}")

    # 4) Tone Transformation
    print("\n[4] Tone Transformation Stage")
    print("-" * 60)
    final_msg: PipelineMessage | None = None

    for gm in grammar_msgs:
        # Convert to tone schema
        tone_msg = PipelineMessage(
            id=gm.id,
            chunk_index=gm.chunk_index,
            text=gm.text,
            event=gm.event,
            is_final=gm.is_final,
            end_of_speech_time=gm.end_of_speech_time
        )
        out = tone_orch.process_message(tone_msg)
        if out is None:
            continue
        if out.event == "PREVIEW_TONE":
            print(f"  PREVIEW_TONE[{out.chunk_index}]: {out.text}")
        elif out.event == "END_TONE":
            final_msg = out

    if final_msg:
        print("\n" + "=" * 60)
        print("FINAL OUTPUT (Ready-to-Use):")
        print("=" * 60)
        print(final_msg.text)
        print("=" * 60)
        if final_msg.end_of_speech_time:
            latency_ms = (time.time() - final_msg.end_of_speech_time) * 1000
            print(f"\nTotal Latency: {latency_ms:.1f}ms")
    else:
        print("\n⚠️  No END_TONE produced; check pipeline wiring.")


if __name__ == "__main__":
    main()
