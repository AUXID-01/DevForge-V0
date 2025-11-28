import asyncio
import numpy as np
import time
import logging
from typing import Optional
from collections import deque
from shared.pipeline_message import PipelineMessage
from .audio_capture import AudioBuffer
from .whisper_engine import WhisperASREngine
from .vad_detector import SpeechSegmentDetector

logger = logging.getLogger(__name__)

class ASRQueueHandler:
    def __init__(self):
        self.asr_engine = WhisperASREngine()
        self.vad = SpeechSegmentDetector(sample_rate=16000, silence_duration_ms=2500)  # 2.5 seconds silence for auto-stop
        self.sessions = {}  # session_id -> session state
        self._prev_transcript = ""  # Track previous transcript to avoid duplicates
    
    def _is_significant_update(self, prev: str, current: str) -> bool:
        """
        Check if current transcript is significantly different from previous.
        Prevents sending duplicate/overlapping transcripts.
        """
        if not prev:
            return True
        
        # Normalize for comparison
        prev_norm = prev.strip().lower()
        curr_norm = current.strip().lower()
        
        # If current is just a prefix of previous, it's not significant
        if prev_norm.startswith(curr_norm) and len(curr_norm) < len(prev_norm) * 0.8:
            return False
        
        # If they're very similar (high overlap), it's not significant
        prev_words = set(prev_norm.split())
        curr_words = set(curr_norm.split())
        
        if not prev_words or not curr_words:
            return True
        
        overlap = len(prev_words & curr_words) / len(prev_words | curr_words)
        
        # Only send if overlap is less than 80% (significant new content)
        return overlap < 0.8
        
    async def process_audio_stream(
        self, 
        session_id: str,
        audio_queue: asyncio.Queue,
        output_queue: asyncio.Queue
    ):
        """
        Process audio chunks from input queue and send PipelineMessages to output queue.
        Uses VAD to detect speech and prevent transcription of silence.
        """
        # Reset context for new session
        self.asr_engine.reset_context()
        self.vad.reset()
        
        audio_buffer = AudioBuffer()
        chunk_counter = 0
        chunk_index = 0
        session_start_time = time.time()
        is_currently_speaking = False
        
        try:
            while True:
                # Get audio chunk from queue
                audio_chunk = await audio_queue.get()
                
                # Check for stop signal
                if audio_chunk is None:
                    break
                
                # Run VAD on the chunk
                vad_result = self.vad.process_audio(audio_chunk)
                
                # Update speaking state
                if vad_result['speech_started']:
                    is_currently_speaking = True
                    audio_buffer.clear()  # Clear buffer when speech starts
                    chunk_counter = 0
                    
                if vad_result['speech_ended']:
                    is_currently_speaking = False
                    
                    # Process any remaining audio in buffer before clearing
                    if len(audio_buffer.buffer) > audio_buffer.chunk_samples:
                        buffer_array = np.array(list(audio_buffer.buffer), dtype=np.float32)
                        rms = np.sqrt(np.mean(buffer_array**2))
                        
                        if rms > 0.005:
                            transcript, metadata = self.asr_engine.transcribe(buffer_array)
                            no_speech_prob = metadata.get('no_speech_prob', 0.0)
                            confidence = metadata.get('confidence', 1.0 - no_speech_prob)
                            
                            if (transcript.strip() and 
                                len(transcript.strip()) > 2 and 
                                no_speech_prob < 0.5 and
                                confidence >= 0.5):
                                
                                # Check if this is a meaningful update
                                prev_text = getattr(self, '_prev_transcript', '')
                                if not prev_text or self._is_significant_update(prev_text, transcript):
                                    msg = PipelineMessage(
                                        id=session_id,
                                        chunk_index=chunk_index,
                                        text=transcript,
                                        event="PART",
                                        is_final=True,  # Mark as final since speech ended
                                        end_of_speech_time=None
                                    )
                                    await output_queue.put(msg)
                                    chunk_index += 1
                                    self._prev_transcript = transcript
                    
                    audio_buffer.clear()
                    chunk_counter = 0
                    
                    # Send AUTO_STOP signal after silence detected
                    stop_msg = PipelineMessage(
                        id=session_id,
                        chunk_index=-2,
                        text="",
                        event="AUTO_STOP",
                        is_final=True,
                        end_of_speech_time=(time.time() - session_start_time) * 1000
                    )
                    await output_queue.put(stop_msg)
                    break  # Exit the loop to stop recording
                
                # Only process audio if speech is detected
                if is_currently_speaking and vad_result['has_speech']:
                    # Add to buffer
                    audio_buffer.add_chunk(audio_chunk)
                    chunk_counter += 1
                    
                    # Transcribe every 1.5 seconds of audio (about 15 chunks at 100ms each) for real-time feel
                    if chunk_counter >= 15 and len(audio_buffer.buffer) > audio_buffer.chunk_samples * 2:
                        chunk_counter = 0
                        
                        # Get current buffer content
                        buffer_array = np.array(list(audio_buffer.buffer), dtype=np.float32)
                        
                        # Only transcribe if we have enough audio data
                        if len(buffer_array) > 0:
                            # Check audio energy before transcribing
                            rms = np.sqrt(np.mean(buffer_array**2))
                            
                            # Only transcribe if audio has meaningful energy
                            if rms > 0.005:
                                # Transcribe
                                transcript, metadata = self.asr_engine.transcribe(buffer_array)
                                
                                # Filter out hallucinations using no_speech_prob
                                no_speech_prob = metadata.get('no_speech_prob', 0.0)
                                
                                # FIX 3: Confidence threshold - only send if confidence is high enough
                                confidence = metadata.get('confidence', 1.0 - no_speech_prob)
                                
                                # Check if transcript looks complete (ends with punctuation or is substantial)
                                is_complete = (
                                    transcript.strip().endswith(('.', '!', '?', ',')) or
                                    len(transcript.split()) >= 5  # At least 5 words
                                )
                                
                                # Send for live transcription if:
                                # - Text exists and has minimum length
                                # - Good confidence (>= 0.6) OR it's a substantial complete segment
                                # - Definitely speech (no_speech_prob < 0.5)
                                should_send = (
                                    transcript.strip() and 
                                    len(transcript.strip()) > 2 and  # Allow shorter chunks for live transcription
                                    no_speech_prob < 0.5 and
                                    (confidence >= 0.6 or (is_complete and confidence >= 0.4))  # Lower threshold for complete segments
                                )
                                
                                if should_send:
                                    # Check if this is a meaningful update (not just repetition)
                                    # Compare with previous transcript to avoid sending duplicates
                                    prev_text = getattr(self, '_prev_transcript', '')
                                    
                                    # Only send if significantly different from previous
                                    if not prev_text or self._is_significant_update(prev_text, transcript):
                                        # Send PART message for live transcription
                                        # Mark as final if it's a complete segment, otherwise partial for live preview
                                        msg = PipelineMessage(
                                            id=session_id,
                                            chunk_index=chunk_index,
                                            text=transcript,
                                            event="PART",
                                            is_final=is_complete,  # Mark as final if complete, partial otherwise
                                            end_of_speech_time=None
                                        )
                                        await output_queue.put(msg)
                                        chunk_index += 1
                                        self._prev_transcript = transcript
                                        
                                        # Clear buffer after sending to avoid overlap
                                        audio_buffer.clear()
                            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[{session_id}] ASR processing error: {e}", exc_info=True)
        finally:
            # Always send END_ASR to ensure pipeline completes
            try:
                end_time_ms = (time.time() - session_start_time) * 1000
                end_msg = PipelineMessage(
                    id=session_id,
                    chunk_index=-1,
                    text="",
                    event="END_ASR",
                    is_final=True,
                    end_of_speech_time=end_time_ms
                )
                await asyncio.wait_for(output_queue.put(end_msg), timeout=5.0)
                logger.info(f"[{session_id}] END_ASR sent (end_of_speech_time={end_time_ms:.1f}ms)")
            except (asyncio.TimeoutError, Exception) as e:
                logger.error(f"[{session_id}] Failed to send END_ASR: {e}")
    
    async def process_with_silence_detection(
        self,
        session_id: str,
        audio_queue: asyncio.Queue,
        output_queue: asyncio.Queue
    ):
        """
        Process audio with silence detection for automatic END_ASR events.
        """
        audio_buffer = AudioBuffer()
        chunk_index = 0
        session_start_time = time.time()
        last_speech_time = time.time()
        silence_threshold = 3.0  # seconds
        
        try:
            while True:
                try:
                    # Get audio chunk with timeout
                    audio_chunk = await asyncio.wait_for(audio_queue.get(), timeout=0.5)
                    
                    if audio_chunk is None:
                        break
                    
                    # Add to buffer
                    audio_buffer.add_chunk(audio_chunk)
                    
                    # Check if we have speech (RMS above threshold)
                    rms = np.sqrt(np.mean(audio_chunk**2))
                    if rms > audio_buffer.silence_threshold:
                        last_speech_time = time.time()
                    
                    # Check if buffer has enough data to transcribe
                    if len(audio_buffer.buffer) >= audio_buffer.sample_rate * 2:  # 2 seconds
                        buffer_array = np.array(list(audio_buffer.buffer), dtype=np.float32)
                        
                        # Check audio energy
                        buffer_rms = np.sqrt(np.mean(buffer_array**2))
                        
                        if buffer_rms > 0.01:
                            # Transcribe
                            transcript, metadata = self.asr_engine.transcribe(buffer_array)
                            
                            # Filter hallucinations
                            no_speech_prob = metadata.get('no_speech_prob', 0.0)
                            
                            if transcript.strip() and no_speech_prob < 0.6:
                                msg = PipelineMessage(
                                    id=session_id,
                                    chunk_index=chunk_index,
                                    text=transcript,
                                    event="PART",
                                    is_final=False,
                                    end_of_speech_time=None
                                )
                                await output_queue.put(msg)
                                chunk_index += 1
                        
                        # Clear buffer after transcription
                        audio_buffer.clear()
                    
                    # Check for silence timeout
                    if time.time() - last_speech_time > silence_threshold:
                        # Send END_ASR and break
                        end_time_ms = (time.time() - session_start_time) * 1000
                        end_msg = PipelineMessage(
                            id=session_id,
                            chunk_index=-1,
                            text="",
                            event="END_ASR",
                            is_final=True,
                            end_of_speech_time=end_time_ms
                        )
                        await output_queue.put(end_msg)
                        break
                        
                except asyncio.TimeoutError:
                    # Check silence timeout
                    if time.time() - last_speech_time > silence_threshold:
                        end_time_ms = (time.time() - session_start_time) * 1000
                        end_msg = PipelineMessage(
                            id=session_id,
                            chunk_index=-1,
                            text="",
                            event="END_ASR",
                            is_final=True,
                            end_of_speech_time=end_time_ms
                        )
                        await output_queue.put(end_msg)
                        break
                        
        except asyncio.CancelledError:
            pass
