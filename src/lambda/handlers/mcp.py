# handlers/mcp.py
from errors import APIException
from utils import tracer


@tracer.capture_method
def mcp_handler(path):
    raise APIException(f"MCP endpoint '{path}' not implemented yet.")
