# constellation_workers.py
import os
import time
from multiprocessing import Queue
from membrane_infra import encode_membrane_frame

def execution_head_node(node_id: int, input_channel: Queue, output_channel: Queue):
    """
    Independent compute node representing 1 of the 4 quadraparallel channels.
    Processes stream telemetry and shapes it back to the core.
    """
    print(f"[Node Head {node_id}] Online. Operating system PID: {os.getpid()}")
    
    while True:
        try:
            # Block safely until data drops into this node's channel
            task = input_channel.get()
            if task is None:  # Sentinel value signaling clean teardown
                print(f"[Node Head {node_id}] Shutting down processing matrix.")
                break
                
            client_id = task.get("client_id")
            payload = task.get("payload", {})
            origin_time = task.get("timestamp", time.time())
            
            # --- Morphism / Computation Layer ---
            # Simulate heavy data alignment calculations for the constellation
            raw_val = sum(ord(char) for char in str(payload))
            morphism_result = (raw_val * node_id) % 360  # Aligned to degrees
            
            # Formulate aligned output envelope
            aligned_output = {
                "node_identity": f"Constellation-Head-{node_id}",
                "process_id": os.getpid(),
                "alignment_status": "SYNCHRONIZED",
                "morphism_index": morphism_result,
                "processing_latency_ms": round((time.time() - origin_time) * 1000, 4)
            }
            
            # Push completed work back up to the main server dispatcher
            output_channel.put({
                "target_client": client_id,
                "data": aligned_output
            })
            
        except Exception as e:
            print(f"[Node Head {node_id} Fault] Data pipeline error: {e}")

