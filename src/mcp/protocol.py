"""MCPProtocol - JSON-RPC 2.0 message codec with Zod-compatible schema validation."""
import json

JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"

class MCPProtocol:
    @staticmethod
    def request(method, params=None, request_id=0):
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "method": method, "params": params or {}}

    @staticmethod
    def notification(method, params=None):
        return {"jsonrpc": JSONRPC_VERSION, "method": method, "params": params or {}}

    @staticmethod
    def response(request_id, result):
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}

    @staticmethod
    def error(request_id, code, message):
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}

    @staticmethod
    def encode(msg):
        return json.dumps(msg)

    @staticmethod
    def decode(raw):
        return json.loads(raw)
