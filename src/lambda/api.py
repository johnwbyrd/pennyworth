from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response, Middleware
from utils import logger
from auth import require_api_key_auth, require_cognito_jwt
from handlers.openai import (
    list_models_handler,
    chat_completions_handler,
    completions_handler,
    embeddings_handler,
)
from handlers.mcp import mcp_handler
from handlers.well_known import well_known_handler
from handlers.protected import protected_handler

app = APIGatewayHttpResolver()

# --- Middleware definitions ---

@Middleware
def api_key_auth_middleware(handler, event, context):
    require_api_key_auth(event)
    return handler(event, context)

@Middleware
def cognito_jwt_auth_middleware(handler, event, context):
    require_cognito_jwt(event)
    return handler(event, context)

# --- OpenAI-compatible endpoints ---

@app.get("/v1/models", middlewares=[api_key_auth_middleware])
def list_models():
    body, status = list_models_handler()
    return Response(status_code=status, content=body)

@app.post("/v1/chat/completions", middlewares=[api_key_auth_middleware])
def chat_completions():
    body, status = chat_completions_handler(app.current_event.json_body or {})
    return Response(status_code=status, content=body)

@app.post("/v1/completions", middlewares=[api_key_auth_middleware])
def completions():
    body, status = completions_handler(app.current_event.json_body or {})
    return Response(status_code=status, content=body)

@app.post("/v1/embeddings", middlewares=[api_key_auth_middleware])
def embeddings():
    body, status = embeddings_handler(app.current_event.json_body or {})
    return Response(status_code=status, content=body)

# --- MCP endpoints ---

@app.any("/v1/mcp/{proxy+}", middlewares=[api_key_auth_middleware])
def mcp():
    path = app.current_event.path
    body, status = mcp_handler(path)
    return Response(status_code=status, content=body)

# --- Parameters endpoints ---

@app.get("/v1/parameters/well-known")
def well_known():
    body, status = well_known_handler()
    return Response(status_code=status, content=body)

@app.get("/v1/parameters/protected", middlewares=[cognito_jwt_auth_middleware])
def protected():
    body, status = protected_handler()
    return Response(status_code=status, content=body)

# --- Catch-all for unsupported endpoints ---

@app.any("/v1/{proxy+}", middlewares=[api_key_auth_middleware])
def not_implemented():
    return Response(status_code=404, content={"error": f"Endpoint '{app.current_event.path}' not implemented."})

# --- Lambda entrypoint ---
def lambda_handler(event, context):
    return app.resolve(event, context) 