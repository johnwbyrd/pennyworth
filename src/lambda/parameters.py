import os
import json
import base64
import urllib.request
from jose import jwt

# Cache JWKS for performance
_JWKS = None

def get_jwks():
    global _JWKS
    if _JWKS is not None:
        return _JWKS
    region = os.environ["AWS_REGION"]
    user_pool_id = os.environ["USER_POOL_ID"]
    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    with urllib.request.urlopen(jwks_url) as resp:
        _JWKS = json.loads(resp.read().decode())
    return _JWKS

def lambda_handler(event, context):
    path = event.get("requestContext", {}).get("http", {}).get("path") or event.get("path", "")
    if path.endswith("/well-known"):
        return well_known_handler(event, context)
    elif path.endswith("/protected"):
        return protected_handler(event, context)
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Not found"})
        }

def well_known_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "UserPoolId": os.environ["USER_POOL_ID"],
            "UserPoolClientId": os.environ["USER_POOL_CLIENT_ID"],
            "IdentityPoolId": os.environ["IDENTITY_POOL_ID"],
            "region": os.environ["AWS_REGION"],
        })
    }

def protected_handler(event, context):
    headers = event.get("headers", {})
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return {"statusCode": 401, "body": json.dumps({"error": "Missing or invalid Authorization header"})}
    token = auth_header.split(" ", 1)[1]
    try:
        jwks = get_jwks()
        region = os.environ["AWS_REGION"]
        user_pool_id = os.environ["USER_POOL_ID"]
        audience = os.environ["USER_POOL_CLIENT_ID"]
        issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        headers_unverified = jwt.get_unverified_header(token)
        kid = headers_unverified["kid"]
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise Exception("Public key not found in JWKS")
        # Validate and decode
        claims = jwt.decode(
            token,
            key,
            algorithms=[key["alg"]],
            audience=audience,
            issuer=issuer,
        )
        # Log claims to CloudWatch
        print(f"Validated JWT claims: {json.dumps(claims)}")
    except Exception as e:
        return {"statusCode": 401, "body": json.dumps({"error": f"Invalid or expired token: {e}"})}
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "ApiKeysTableName": os.environ["API_KEYS_TABLE"],
        })
    }

# No changes needed for now, but add a note for future imports if this module needs to use shared utils/auth/model_router.
# from utils import json_response  # Example for future use
# from auth import validate_api_key 