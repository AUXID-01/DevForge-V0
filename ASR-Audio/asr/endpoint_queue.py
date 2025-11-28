import asyncio
import numpy as np
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from shared.pipeline_message import PipelineMessage
from .asr_queue_handler import ASRQueueHandler

asr_handler = ASRQueueHandler()

async def asr_stream_with_queue(websocket: WebSocket):
    """
    WebSocket endpoint that uses queue-based processing with PipelineMessage schema.
    """
    await websocket.accept()
    
    # Generate session ID
    session_id = f"utt_{uuid.uuid4().hex[:8]}"
    
    # Create queues
    audio_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    
    # Start ASR processing task
    asr_task = asyncio.create_task(
        asr_handler.process_audio_stream(session_id, audio_queue, output_queue)
    )
    
    # Start output sender task
    async def send_outputs():
        try:
            while True:
                msg = await output_queue.get()
                try:
                    # Check if websocket is still connected
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_json(msg.model_dump())
                    else:
                        break
                except Exception as send_err:
                    print(f"Error sending message: {send_err}")
                    break
                
                # If END_ASR, we can stop
                if msg.event == "END_ASR":
                    break
        except Exception as e:
            print(f"Error in output sender: {e}")
    
    sender_task = asyncio.create_task(send_outputs())
    
    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            
            # Put in audio queue
            await audio_queue.put(audio_chunk)
            
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
    finally:
        # Signal end of audio stream
        await audio_queue.put(None)
        
        # Wait for tasks to complete
        try:
            await asyncio.wait_for(asr_task, timeout=5.0)
            await asyncio.wait_for(sender_task, timeout=5.0)
        except asyncio.TimeoutError:
            asr_task.cancel()
            sender_task.cancel()


async def asr_stream_with_silence_detection(websocket: WebSocket):
    """
    WebSocket endpoint with automatic END_ASR on silence detection.
    """
    await websocket.accept()
    
    # Generate session ID
    session_id = f"utt_{uuid.uuid4().hex[:8]}"
    
    # Create queues
    audio_queue = asyncio.Queue()
    output_queue = asyncio.Queue()
    
    # Start ASR processing task with silence detection
    asr_task = asyncio.create_task(
        asr_handler.process_with_silence_detection(session_id, audio_queue, output_queue)
    )
    
    # Start output sender task
    async def send_outputs():
        try:
            while True:
                msg = await output_queue.get()
                try:
                    await websocket.send_json(msg.model_dump())
                except Exception as send_err:
                    print(f"Error sending message: {send_err}")
                    break
                
                # If END_ASR, we can stop
                if msg.event == "END_ASR":
                    break
        except Exception as e:
            print(f"Error in output sender: {e}")
    
    sender_task = asyncio.create_task(send_outputs())
    
    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            
            # Put in audio queue
            await audio_queue.put(audio_chunk)
            
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
    finally:
        # Signal end of audio stream
        await audio_queue.put(None)
        
        # Wait for tasks to complete
        try:
            await asyncio.wait_for(asr_task, timeout=5.0)
            await asyncio.wait_for(sender_task, timeout=5.0)
        except asyncio.TimeoutError:
            asr_task.cancel()
            sender_task.cancel()
