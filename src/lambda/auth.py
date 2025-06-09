# Authentication helpers for API key validation

import os
import json
import base64
import urllib.request
from jose import jwt
from utils import logger, tracer
from errors import ForbiddenException
import boto3
from botocore.exceptions import ClientError
from src.shared.constants import *


# --- Robust Bearer Token Extraction Helper ---
@tracer.capture_method
def extract_bearer_token(headers):
    """
    Extracts a Bearer token from the Authorization header.
    - Accepts both 'Authorization' and 'authorization' header names (HTTP headers are case-insensitive).
    - Accepts both 'Bearer' and 'bearer' (case-insensitive) as the scheme, for client compatibility.
    - Requires exactly two parts: scheme and token (e.g., 'Bearer <token>').
    - Rejects headers with missing, empty, or run-on tokens (e.g., 'Bearer', 'Bearer ', 'Bearer token extra').
    - Trims whitespace from the token.
    - Returns the token string if valid, or None if invalid/malformed.
    """
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header:
        return None
    parts = auth_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    if not token:
        return None
    return token


# --- API Key Authentication ---
@tracer.capture_method
def require_api_key_auth(event):
    """
    Centralized API key authentication for all endpoints.
    Extracts the API key from the Authorization header (Bearer) or x-api-key header.
    For now, always raises an exception (unauthorized).
    """
    headers = event.get("headers", {})
    api_key = extract_bearer_token(headers)
    if not api_key:
        raise ForbiddenException("Missing or invalid API key in Authorization header.")
    # TODO: Implement real API key validation (Cognito lookup)
    raise ForbiddenException("Unauthorized: API key validation not implemented.")


# Cognito JWT validation helpers
_JWKS = None


@tracer.capture_method
def get_jwks():
    global _JWKS
    if _JWKS is not None:
        return _JWKS
    region = PENNYWORTH_AWS_REGION
    user_pool_id = PENNYWORTH_USER_POOL_ID
    jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
    try:
        with urllib.request.urlopen(jwks_url) as resp:
            _JWKS = json.loads(resp.read().decode())
        return _JWKS
    except Exception as e:
        logger.error(f"Failed to fetch or parse JWKS from {jwks_url}: {e}")
        raise Exception(f"Unable to fetch or parse Cognito JWKS: {e}")


@tracer.capture_method
def require_cognito_jwt(event):
    headers = event.get("headers", {})
    token = extract_bearer_token(headers)
    if not token:
        raise ForbiddenException("Missing or invalid Authorization header.")
    region = PENNYWORTH_AWS_REGION
    user_pool_id = PENNYWORTH_USER_POOL_ID
    audience = PENNYWORTH_USER_POOL_CLIENT_ID
    if not region or not user_pool_id or not audience:
        raise ForbiddenException(
            "Cognito JWT validation misconfigured: missing region, user pool ID, or audience."
        )
    try:
        jwks = get_jwks()
        issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        headers_unverified = jwt.get_unverified_header(token)
        kid = headers_unverified["kid"]
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise ForbiddenException("Public key not found in JWKS.")
        # Validate and decode the JWT
        claims = jwt.decode(
            token,
            key,
            algorithms=[key["alg"]],
            audience=audience,
            issuer=issuer,
        )
        logger.info(f"Validated Cognito JWT claims: {json.dumps(claims)}")
        return claims
    except Exception as e:
        raise ForbiddenException(f"Invalid or expired Cognito JWT: {e}")


@tracer.capture_method
def get_user_boto3_session(event):
    """
    Given a Lambda event, extract the Cognito JWT and exchange it for AWS credentials
    using the Cognito Identity Pool. Returns a boto3.Session using those credentials.
    Explicitly validates the JWT before exchanging.
    """
    # Explicitly validate the JWT
    require_cognito_jwt(event)
    headers = event.get("headers", {})
    token = extract_bearer_token(headers)
    if not token:
        raise ForbiddenException("Missing or invalid Authorization header.")

    identity_pool_id = PENNYWORTH_IDENTITY_POOL_ID
    region = PENNYWORTH_AWS_REGION
    user_pool_id = PENNYWORTH_USER_POOL_ID
    if not identity_pool_id or not region or not user_pool_id:
        raise ForbiddenException("Missing Cognito Identity Pool configuration.")

    cognito_identity = boto3.client("cognito-identity", region_name=region)
    try:
        resp = cognito_identity.get_id(
            IdentityPoolId=identity_pool_id,
            Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": token},
        )
        identity_id = resp["IdentityId"]
        creds_resp = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={f"cognito-idp.{region}.amazonaws.com/{user_pool_id}": token},
        )
        creds = creds_resp["Credentials"]
    except ClientError as e:
        raise ForbiddenException("Could not obtain AWS credentials for user.")

    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )
