"""
Unified Streaming Pipeline Orchestrator

Connects all stages:
ASR → Disfluency → Grammar → Tone

Uses async queues for streaming with <1.5s latency.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional, Dict
import time
import logging

# Add paths for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "ASR-Audio"))
sys.path.insert(0, str(project_root / "DEvf"))
# Add speech-dictation-engine/src to path so imports work correctly
speech_engine_src = project_root / "speech-dictation-engine" / "src"
sys.path.insert(0, str(speech_engine_src))
sys.path.insert(0, str(project_root / "toneAndOrchestration"))

from shared.pipeline_message import PipelineMessage as ASRPipelineMessage
from disfluency_module.worker import DisfluencyWorker
from disfluency_module.schema import PipelineMessage as DisfluencyPipelineMessage
from grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage as GrammarPipelineMessage
from orchestrator.orchestrator import PipelineOrchestrator
from schemas.pipeline_message import PipelineMessage as TonePipelineMessage
from asr.asr_queue_handler import ASRQueueHandler

# Import late fusion
try:
    from late_fusion import LateFusionProcessor
except ImportError:
    # Fallback if import fails
    class LateFusionProcessor:
        def process(self, text: str) -> str:
            return text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UnifiedPipelineOrchestrator:
    """
    Unified streaming pipeline that connects:
    ASR → Disfluency → Grammar → Tone
    
    Uses async queues for low-latency streaming processing.
    """
    
    def __init__(self, tone_mode: str = "neutral"):
        self.tone_mode = tone_mode
        
        # Initialize components
        self.asr_handler = ASRQueueHandler()
        
        # Grammar engine (shared across sessions)
        self.grammar_engine = GrammarFormattingEngine()
        
        # Tone orchestrator (shared across sessions)
        self.tone_orchestrator = PipelineOrchestrator(tone_mode=tone_mode)
        
        # Session state tracking (disfluency workers per session)
        self.disfluency_workers: Dict[str, DisfluencyWorker] = {}
        
        # Late fusion processor (final cleanup)
        self.late_fusion = LateFusionProcessor()
        
        logger.info(f"✅ Unified Pipeline Orchestrator initialized (tone_mode={tone_mode})")
    
    def _convert_message(self, msg, target_class):
        """Convert PipelineMessage between different module schemas"""
        if isinstance(msg, target_class):
            return msg
        
        # Convert to dict and create new instance
        data = {
            "id": msg.id,
            "chunk_index": msg.chunk_index,
            "text": msg.text,
            "event": msg.event,
            "is_final": msg.is_final,
            "end_of_speech_time": msg.end_of_speech_time
        }
        return target_class(**data)
    
    async def process_disfluency(self, session_id: str, msg: ASRPipelineMessage) -> DisfluencyPipelineMessage:
        """Process message through disfluency stage with latency tracking"""
        start_time = time.time()
        
        # Convert to disfluency schema
        disfluency_msg = self._convert_message(msg, DisfluencyPipelineMessage)
        
        # Get or create worker for this session (maintains context)
        if session_id not in self.disfluency_workers:
            output_queue = []
            self.disfluency_workers[session_id] = DisfluencyWorker([], output_queue)
        
        worker = self.disfluency_workers[session_id]
        output_queue = worker.output_queue
        
        # Clear output queue before processing (if it's a list)
        if isinstance(output_queue, list):
            output_queue.clear()
        
        # Process message (sync operation, but fast)
        worker.process_message(disfluency_msg)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Get result from output queue
        if isinstance(output_queue, list) and len(output_queue) > 0:
            result = output_queue[0]
            # Add latency info to result (store in a custom attribute or pass through)
            # Clean up worker if END_CLEAN
            if result.event == "END_CLEAN":
                self.disfluency_workers.pop(session_id, None)
            # Store latency in a way we can access later
            result._disfluency_latency_ms = latency_ms
            return result
        else:
            # If no output, create a pass-through message
            disfluency_msg._disfluency_latency_ms = latency_ms
            return disfluency_msg
    
    async def process_grammar(self, msg: DisfluencyPipelineMessage) -> GrammarPipelineMessage:
        """Process message through grammar stage with latency tracking"""
        start_time = time.time()
        
        # Convert to grammar schema
        grammar_msg = self._convert_message(msg, GrammarPipelineMessage)
        
        # Process through grammar engine (sync operation, but fast)
        result = self.grammar_engine.process_message(grammar_msg)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        result._grammar_latency_ms = latency_ms
        
        # Preserve disfluency latency if it exists
        if hasattr(msg, '_disfluency_latency_ms'):
            result._disfluency_latency_ms = msg._disfluency_latency_ms
        
        return result
    
    async def process_tone(self, msg: GrammarPipelineMessage) -> Optional[TonePipelineMessage]:
        """Process message through tone stage with latency tracking"""
        start_time = time.time()
        
        # Convert to tone schema
        tone_msg = self._convert_message(msg, TonePipelineMessage)
        
        # Process through tone orchestrator
        result = self.tone_orchestrator.process_message(tone_msg)
        
        if result:
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            result._tone_latency_ms = latency_ms
            
            # Preserve previous stage latencies if they exist
            if hasattr(msg, '_disfluency_latency_ms'):
                result._disfluency_latency_ms = msg._disfluency_latency_ms
            if hasattr(msg, '_grammar_latency_ms'):
                result._grammar_latency_ms = msg._grammar_latency_ms
            
            # Log tone transformation for debugging
            if result.event == "END_TONE":
                logger.info(f"[{msg.id}] Tone transformation applied (mode={self.tone_mode}): '{msg.text[:50]}...' → '{result.text[:50]}...'")
        
        return result
    
    async def process_full_pipeline(
        self,
        session_id: str,
        audio_queue: asyncio.Queue,
        output_queue: asyncio.Queue
    ):
        """
        Main pipeline processing loop.
        
        Processes audio chunks through:
        ASR → Disfluency → Grammar → Tone
        
        All stages run in streaming mode with async queues.
        """
        # Create queues for each stage
        asr_output_queue = asyncio.Queue()
        disfluency_output_queue = asyncio.Queue()
        grammar_output_queue = asyncio.Queue()
        
        # Start ASR processing task
        asr_task = asyncio.create_task(
            self.asr_handler.process_audio_stream(session_id, audio_queue, asr_output_queue)
        )
        
        # Stage 1: ASR → Disfluency
        async def asr_to_disfluency():
            try:
                while True:
                    msg = await asr_output_queue.get()
                    
                    # Track ASR latency if available
                    asr_latency = None
                    if hasattr(msg, 'latency_ms'):
                        asr_latency = msg.latency_ms
                    elif msg.event == "END_ASR" and msg.end_of_speech_time:
                        # Calculate ASR latency from end_of_speech_time
                        asr_latency = (time.time() * 1000) - msg.end_of_speech_time
                    
                    # Process through disfluency (runs sync but fast)
                    disfluency_result = await self.process_disfluency(session_id, msg)
                    
                    # Store ASR latency if available
                    if asr_latency is not None:
                        disfluency_result._asr_latency_ms = asr_latency
                    
                    await disfluency_output_queue.put(disfluency_result)
                    
                    # Check for end - AUTO_STOP should also trigger END_ASR flow
                    if msg.event == "END_ASR" or msg.event == "AUTO_STOP":
                        # AUTO_STOP should be treated like END_ASR
                        if msg.event == "AUTO_STOP":
                            # Convert AUTO_STOP to END_ASR for downstream processing
                            disfluency_result.event = "END_ASR"
                        break
            except Exception as e:
                logger.error(f"Error in ASR→Disfluency stage: {e}", exc_info=True)
        
        # Stage 2: Disfluency → Grammar (process immediately for correct ordering)
        async def disfluency_to_grammar():
            try:
                while True:
                    msg = await disfluency_output_queue.get()
                    
                    # Process immediately to maintain order
                    grammar_result = await self.process_grammar(msg)
                    await grammar_output_queue.put(grammar_result)
                    
                    # Check for end
                    if msg.event == "END_CLEAN":
                        break
                    
            except Exception as e:
                logger.error(f"Error in Disfluency→Grammar stage: {e}", exc_info=True)
        
        # Stage 3: Grammar → Tone → Late Fusion → Output
        async def grammar_to_tone():
            try:
                while True:
                    msg = await grammar_output_queue.get()
                    
                    # Process through tone (runs sync but fast)
                    tone_result = await self.process_tone(msg)
                    
                    if tone_result:
                        # Apply late fusion for final output
                        if tone_result.event == "END_TONE":
                            # Final output - apply late fusion cleanup
                            if tone_result.text:
                                fused_text = self.late_fusion.process(tone_result.text)
                                tone_result.text = fused_text
                                logger.info(f"[{msg.id}] Final output ready: '{tone_result.text[:100]}...'")
                            else:
                                logger.warning(f"[{msg.id}] END_TONE with empty text")
                        
                        await output_queue.put(tone_result)
                    
                    # Check for end
                    if msg.event == "END_GRAMMAR":
                        # Ensure END_TONE is sent even if tone_result is None
                        if not tone_result or tone_result.event != "END_TONE":
                            logger.warning(f"[{msg.id}] END_GRAMMAR received but no END_TONE generated, creating fallback")
                            # Create fallback END_TONE message
                            fallback_msg = TonePipelineMessage(
                                id=msg.id,
                                chunk_index=0,
                                text="",
                                event="END_TONE",
                                is_final=True,
                                end_of_speech_time=msg.end_of_speech_time
                            )
                            await output_queue.put(fallback_msg)
                        break
            except Exception as e:
                logger.error(f"Error in Grammar→Tone stage: {e}", exc_info=True)
                # On error, try to send END_TONE anyway
                try:
                    fallback_msg = TonePipelineMessage(
                        id=session_id,
                        chunk_index=0,
                        text="",
                        event="END_TONE",
                        is_final=True,
                        end_of_speech_time=None
                    )
                    await output_queue.put(fallback_msg)
                except:
                    pass
        
        # Start all pipeline stages
        stage1_task = asyncio.create_task(asr_to_disfluency())
        stage2_task = asyncio.create_task(disfluency_to_grammar())
        stage3_task = asyncio.create_task(grammar_to_tone())
        
        # Wait for ASR to complete
        try:
            await asr_task
        except Exception as e:
            logger.error(f"ASR task error: {e}", exc_info=True)
        
        # Wait for all stages to complete
        try:
            await asyncio.gather(stage1_task, stage2_task, stage3_task, return_exceptions=True)
        except Exception as e:
            logger.error(f"Pipeline stage error: {e}")
        
        logger.info(f"[{session_id}] Pipeline processing complete")

