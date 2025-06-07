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
import os
from version import API_SEMANTIC_VERSION
from aws_lambda_powertools.event_handler.api_gateway import Response as PowertoolsResponse
from errors import APIException, ForbiddenException, BadRequestException, NotFoundException

app = APIGatewayHttpResolver()

PENNYWORTH_API_VERSION = os.environ.get("PENNYWORTH_API_VERSION", "v1")
API_VER = PENNYWORTH_API_VERSION  # Local alias for brevity
PENNYWORTH_BUILD_ID = os.environ.get("PENNYWORTH_BUILD_ID", "unknown")

# --- Middleware definitions ---

@Middleware
def api_key_auth_middleware(handler, event, context):
    require_api_key_auth(event)
    return handler(event, context)

@Middleware
def cognito_jwt_auth_middleware(handler, event, context):
    require_cognito_jwt(event)
    return handler(event, context)

def wrap_handler(handler, *args, **kwargs):
    body, status = handler(*args, **kwargs)
    return Response(status_code=status, content=body)

# --- OpenAI-compatible endpoints ---

@app.get(f"/{API_VER}/models", middlewares=[api_key_auth_middleware])
def list_models():
    return wrap_handler(list_models_handler)

@app.post(f"/{API_VER}/chat/completions", middlewares=[api_key_auth_middleware])
def chat_completions():
    return wrap_handler(chat_completions_handler, app.current_event.json_body or {})

@app.post(f"/{API_VER}/completions", middlewares=[api_key_auth_middleware])
def completions():
    return wrap_handler(completions_handler, app.current_event.json_body or {})

@app.post(f"/{API_VER}/embeddings", middlewares=[api_key_auth_middleware])
def embeddings():
    return wrap_handler(embeddings_handler, app.current_event.json_body or {})

# --- MCP endpoints ---

@app.any(f"/{API_VER}/mcp/{{proxy+}}", middlewares=[api_key_auth_middleware])
def mcp():
    return wrap_handler(mcp_handler, app.current_event.path)

# --- Parameters endpoints ---

@app.get(f"/{API_VER}/parameters/well-known")
def well_known():
    return wrap_handler(well_known_handler)

@app.get(f"/{API_VER}/parameters/protected", middlewares=[cognito_jwt_auth_middleware])
def protected():
    return wrap_handler(protected_handler)

@app.get(f"/{API_VER}/version", middlewares=[api_key_auth_middleware])
def version():
    return Response(status_code=200, content={
        "Version": API_VER,
        "SemanticVersion": API_SEMANTIC_VERSION,
        "BuildId": PENNYWORTH_BUILD_ID
    })

# --- Catch-all for unsupported endpoints ---

@app.any(f"/{API_VER}/{{proxy+}}", middlewares=[api_key_auth_middleware])
def not_implemented():
    return Response(status_code=404, content={"error": f"Endpoint '{app.current_event.path}' not implemented."})

# --- Exception handlers ---

@app.exception_handler(APIException)
def handle_api_exception(ex):
    return PowertoolsResponse(
        status_code=ex.status_code,
        content={"error": str(ex)}
    )

# --- Lambda entrypoint ---
def lambda_handler(event, context):
    return app.resolve(event, context) 