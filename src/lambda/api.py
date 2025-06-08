import os
import json

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.exceptions import NotFoundError

from utils import logger
from errors import APIException, ForbiddenException, BadRequestException, NotFoundException
from auth import require_api_key_auth, require_cognito_jwt, get_user_boto3_session
from handlers.openai import (
    list_models_handler,
    chat_completions_handler,
    completions_handler,
    embeddings_handler,
)
from handlers.mcp import mcp_handler
from handlers.well_known import well_known_handler
from handlers.protected import protected_handler
from handlers.version import version_handler
from version import API_SEMANTIC_VERSION
from handlers.users import (
    create_user_handler,
    get_user_handler,
    update_user_handler,
    delete_user_handler,
    list_users_handler,
    create_or_rotate_apikey_handler,
    revoke_apikey_handler,
    get_apikey_status_handler,
)

app = APIGatewayRestResolver()

PENNYWORTH_API_VERSION = os.environ.get("PENNYWORTH_API_VERSION", "v1")
API_VER = PENNYWORTH_API_VERSION  # Local alias for brevity
PENNYWORTH_BUILD_ID = os.environ.get("PENNYWORTH_BUILD_ID", "unknown")

# --- Middleware definitions ---
def api_key_auth_middleware(app, next_middleware):
    """
    Enforces API key authentication for protected endpoints.
    If the API key is missing or invalid, raises ForbiddenException (403).
    """
    require_api_key_auth(app.current_event.raw_event)
    return next_middleware(app)

def cognito_jwt_auth_middleware(app, next_middleware):
    """
    Enforces Cognito JWT authentication for protected endpoints.
    If the JWT is missing, invalid, or expired, raises ForbiddenException (403).
    """
    require_cognito_jwt(app.current_event.raw_event)
    return next_middleware(app)

def user_session_middleware(app, next_middleware):
    """
    Validates Cognito JWT and attaches a user-context boto3 session to the event.
    If authentication or session acquisition fails, raises ForbiddenException (403).
    """
    require_cognito_jwt(app.current_event.raw_event)
    session = get_user_boto3_session(app.current_event.raw_event)
    app.current_event.raw_event["user_session"] = session
    return next_middleware(app)

def public_auth_middleware(app, next_middleware):
    """
    Allows all requests (no authentication enforced).
    Use for public endpoints that do not require authentication.
    """
    return next_middleware(app)

# Register global middlewares (order matters if you want stacking)
# Example: app.use([user_session_middleware, ...])
# Add or remove as needed for your routes
app.use([
    # Add global middlewares here if needed
])

# --- SafeResponse utility ---
def SafeResponse(*, status_code, body=None, message=None, exception=None, **kwargs):
    """
    Ensures the response body is a JSON string for API Gateway, logs the response, and can handle normal payloads, messages, or exceptions.
    This is needed because API Gateway requires a string body and Powertools serialization is unreliable across versions.
    """
    if exception is not None:
        response_body = {"error": str(exception)}
        logger.warning({"status": status_code, "error": str(exception)})
    elif message is not None:
        response_body = {"message": message}
        logger.info({"status": status_code, "message": message})
    elif body is not None:
        response_body = body
        logger.info({"status": status_code, "body": body})
    else:
        response_body = {}
        logger.info({"status": status_code, "body": {}})

    if not isinstance(response_body, str):
        response_body = json.dumps(response_body)

    return Response(status_code=status_code, body=response_body, **kwargs)

# --- Handler utility ---
def wrap_handler(handler, *args, **kwargs):
    """
    Calls the given handler function, expecting a (body, status) tuple,
    and returns a properly formatted Response for API Gateway.
    This reduces boilerplate in endpoint functions.
    """
    body, status = handler(*args, **kwargs)
    logger.info({"msg": "wrap_handler returning", "body": body, "status": status})
    return SafeResponse(status_code=status, body=body)

# --- OpenAI-compatible endpoints ---

@app.get(f"/{API_VER}/models")
def list_models():
    return wrap_handler(list_models_handler)

@app.post(f"/{API_VER}/chat/completions")
def chat_completions():
    return wrap_handler(chat_completions_handler, app.current_event.json_body or {})

@app.post(f"/{API_VER}/completions")
def completions():
    return wrap_handler(completions_handler, app.current_event.json_body or {})

@app.post(f"/{API_VER}/embeddings")
def embeddings():
    return wrap_handler(embeddings_handler, app.current_event.json_body or {})

# --- MCP endpoints ---

@app.route(f"/{API_VER}/mcp/{{proxy+}}", method=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def mcp():
    return wrap_handler(mcp_handler, app.current_event.path)

# --- Parameters endpoints ---

@app.get(f"/{API_VER}/parameters/well-known")
def well_known():
    return wrap_handler(well_known_handler)

@app.get(f"/{API_VER}/parameters/protected")
def protected():
    return wrap_handler(protected_handler)

@app.get(f"/{API_VER}/version")
def version():
    return wrap_handler(version_handler)

# --- Users endpoints ---

@app.post(f"/{API_VER}/users")
def create_user():
    return wrap_handler(create_user_handler, app.current_event, app.current_event.json_body or {})

@app.get(f"/{API_VER}/users/{{user_id}}")
def get_user(user_id):
    return wrap_handler(get_user_handler, app.current_event, user_id)

@app.put(f"/{API_VER}/users/{{user_id}}")
def update_user(user_id):
    return wrap_handler(update_user_handler, app.current_event, user_id, app.current_event.json_body or {})

@app.delete(f"/{API_VER}/users/{{user_id}}")
def delete_user(user_id):
    return wrap_handler(delete_user_handler, app.current_event, user_id)

@app.get(f"/{API_VER}/users")
def list_users():
    return wrap_handler(list_users_handler, app.current_event)

@app.post(f"/{API_VER}/users/{{user_id}}/apikey")
def create_or_rotate_apikey(user_id):
    return wrap_handler(create_or_rotate_apikey_handler, app.current_event, user_id)

@app.delete(f"/{API_VER}/users/{{user_id}}/apikey")
def revoke_apikey(user_id):
    return wrap_handler(revoke_apikey_handler, app.current_event, user_id)

@app.get(f"/{API_VER}/users/{{user_id}}/apikey")
def get_apikey_status(user_id):
    return wrap_handler(get_apikey_status_handler, app.current_event, user_id)

# --- Catch-all for unsupported endpoints ---

@app.not_found
def not_found(e: NotFoundError):
    return SafeResponse(status_code=404, message=str(e))

# --- Exception handlers ---

@app.exception_handler(APIException)
def handle_api_exception(ex):
    return SafeResponse(status_code=ex.status_code, exception=ex)

# --- Lambda entrypoint ---
def lambda_handler(event, context):
    logger.info({"msg": "lambda_handler invoked", "event": event})
    try:
        response = app.resolve(event, context)
        logger.info({"msg": "lambda_handler returning", "response": str(response)})
        return response
    except Exception as e:
        logger.exception({"msg": "Exception in lambda_handler", "error": str(e)})
        raise 