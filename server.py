# server.py
import asyncio
import multiprocessing
import sys
from membrane_infra import HOST, PORT, QUAD_NODES, encode_membrane_frame, decode_membrane_frame
from constellation_workers import execution_head_node

class OmegaBetaMembraneServer:
    def __init__(self):
        # Create dedicated safe communication lanes for each quad-node
        self.to_workers = [multiprocessing.Queue() for _ in range(QUAD_NODES)]
        self.from_workers = multiprocessing.Queue()
        self.worker_pool = []
        self.connected_terminals = {}
        self.balancer_index = 0

    def establish_quadraparallel_morphism(self):
        """Spawns the 4 underlying isolated compute execution heads."""
        print("[System init] Aligning quadraparallel multiprocessing heads...")
        for i in range(QUAD_NODES):
            proc = multiprocessing.Process(
                target=execution_head_node,
                args=(i, self.to_workers[i], self.from_workers)
            )
            proc.daemon = True  # Inherits lifecycle constraints of parent process
            proc.start()
            self.worker_pool.append(proc)

    async def run_output_delivery_loop(self):
        """Continuously pulls calculated frames from workers and writes to network sockets."""
        while True:
            # Non-blocking pull from the multi-processing queue
            while not self.from_workers.empty():
                try:
                    msg = self.from_workers.get_nowait()
                    target_client = msg.get("target_client")
                    aligned_data = msg.get("data")
                    
                    if target_client in self.connected_terminals:
                        writer = self.connected_terminals[target_client]
                        frame = encode_membrane_frame({"event": "METRIC_ALIGNMENT", "payload": aligned_data})
                        writer.write(frame)
                        await writer.drain()
                except Exception as e:
                    print(f"[Core Dispatch Error] Failed to rout packet: {e}")
            
            await asyncio.sleep(0.001)  # Micro-yield to maintain CPU sanity

    async def connection_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Manages bidirectional streaming data safely for every unique terminal."""
        terminal_id = f"Terminal-{id(reader)}"
        self.connected_terminals[terminal_id] = writer
        print(f"[Membrane Connected] {terminal_id} linked into active stream.")

        try:
            while True:
                # Continuous streaming input fetching
                data_line = await reader.readline()
                if not data_line:
                    break  # Connection dropped cleanly
                
                incoming_payload = decode_membrane_frame(data_line)
                if "error" in incoming_payload:
                    continue
                
                # Round-robin allocation to balance computation perfectly across all 4 nodes
                selected_node = self.balancer_index % QUAD_NODES
                self.balancer_index += 1
                
                # Pass tasks through the multiprocessing membrane queue
                self.to_workers[selected_node].put({
                    "client_id": terminal_id,
                    "payload": incoming_payload,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Membrane Connection Exception] {terminal_id}: {e}")
        finally:
            print(f"[Membrane Severed] Cleanly removing {terminal_id}")
            self.connected_terminals.pop(terminal_id, None)
            writer.close()
            await writer.wait_closed()

    async def main(self):
        self.establish_quadraparallel_morphism()
        
        server = await asyncio.start_server(self.connection_handler, HOST, PORT)
        print(f"[Sky Protocol Initialized] Matrix serving on tcp://{HOST}:{PORT}")
        
        # Concurrently coordinate asynchronous client handling and multiprocessing output delivery
        await asyncio.gather(
            server.serve_forever(),
            self.run_output_delivery_loop()
        )

    def shutdown(self):
        print("\n[Teardown initiated] Collapsing membrane safely...")
        for q in self.to_workers:
            q.put(None)  # Deploy poison pills to shut down worker loops cleanly
        for proc in self.worker_pool:
            proc.join(timeout=1.0)
            proc.terminate()
        print("[System Offline] All resources reclaimed cleanly.")

if __name__ == "__main__":
    engine = OmegaBetaMembraneServer()
    try:
        asyncio.run(engine.main())
    except KeyboardInterrupt:
        engine.shutdown()
        sys.exit(0)
      
