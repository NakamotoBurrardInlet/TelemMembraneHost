# membrane_infra.py
import json

HOST = "127.0.0.1"
PORT = 9999
QUAD_NODES = 4  # The 4 parallel constellation processing heads

def encode_membrane_frame(payload: dict) -> bytes:
    """Serializes and seals a data packet with a newline delimiter."""
    try:
        return (json.dumps(payload) + "\n").encode("utf-8")
    except (TypeError, ValueError) as e:
        return (json.dumps({"error": "Serialization Failed", "details": str(e)}) + "\n").encode("utf-8")

def decode_membrane_frame(raw_bytes: bytes) -> dict:
    """Safely extracts a structured payload from the incoming stream stream."""
    try:
        cleaned = raw_bytes.decode("utf-8").strip()
        return json.loads(cleaned) if cleaned else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"error": "Malformed Frame Received"}
      
