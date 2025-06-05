import boto3
import botocore
import requests
import os
from typing import Tuple, Optional

# Placeholder: Fill in these values or load from environment/config
COGNITO_USER_POOL_ID = os.environ.get("PENNYWORTH_COGNITO_USER_POOL_ID", "<user-pool-id>")
COGNITO_CLIENT_ID = os.environ.get("PENNYWORTH_COGNITO_CLIENT_ID", "<user-pool-client-id>")
COGNITO_IDENTITY_POOL_ID = os.environ.get("PENNYWORTH_COGNITO_IDENTITY_POOL_ID", "<identity-pool-id>")
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")


def cognito_login(username: str, password: str) -> str:
    """
    Authenticate a user with Cognito User Pool and return the ID token.
    """
    client = boto3.client("cognito-idp", region_name=AWS_REGION)
    try:
        resp = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=COGNITO_CLIENT_ID,
        )
        id_token = resp["AuthenticationResult"]["IdToken"]
        return id_token
    except botocore.exceptions.ClientError as e:
        print(f"[auth] Cognito login failed: {e}")
        raise


def get_aws_credentials_from_cognito(id_token: str) -> dict:
    """
    Exchange a Cognito ID token for temporary AWS credentials via the Identity Pool.
    Returns a dict with AccessKeyId, SecretKey, SessionToken.
    """
    client = boto3.client("cognito-identity", region_name=AWS_REGION)
    try:
        # Get the identity id
        identity_resp = client.get_id(
            IdentityPoolId=COGNITO_IDENTITY_POOL_ID,
            Logins={
                f"cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}": id_token
            },
        )
        identity_id = identity_resp["IdentityId"]
        # Get credentials
        creds_resp = client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={
                f"cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}": id_token
            },
        )
        return creds_resp["Credentials"]
    except botocore.exceptions.ClientError as e:
        print(f"[auth] Failed to get AWS credentials: {e}")
        raise

# Example usage (to be called from CLI):
# id_token = cognito_login(username, password)
# creds = get_aws_credentials_from_cognito(id_token) 