import boto3
import botocore
import os
import json
from typing import Optional

# These will be loaded from the CLI config secret at runtime
COGNITO_USER_POOL_ID = None
COGNITO_CLIENT_ID = None
COGNITO_IDENTITY_POOL_ID = None
AWS_REGION = None


def load_auth_config(config: dict):
    global COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID, COGNITO_IDENTITY_POOL_ID, AWS_REGION
    COGNITO_USER_POOL_ID = config["UserPoolId"]
    COGNITO_CLIENT_ID = config["UserPoolClientId"]
    COGNITO_IDENTITY_POOL_ID = config["IdentityPoolId"]
    AWS_REGION = config.get("region", os.environ.get("AWS_REGION", "us-west-2"))


def cognito_login(username: str, password: str) -> str:
    """
    Authenticate a user with Cognito User Pool and return the ID token. Handles MFA if required.
    """
    client = boto3.client("cognito-idp", region_name=AWS_REGION)
    try:
        resp = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=COGNITO_CLIENT_ID,
        )
        if "ChallengeName" in resp and resp["ChallengeName"] in ("SMS_MFA", "SOFTWARE_TOKEN_MFA"):
            mfa_code = input(f"Enter MFA code ({resp['ChallengeName']}): ")
            mfa_resp = client.respond_to_auth_challenge(
                ClientId=COGNITO_CLIENT_ID,
                ChallengeName=resp["ChallengeName"],
                Session=resp["Session"],
                ChallengeResponses={
                    "USERNAME": username,
                    ("SMS_MFA_CODE" if resp["ChallengeName"] == "SMS_MFA" else "SOFTWARE_TOKEN_MFA_CODE"): mfa_code,
                },
            )
            id_token = mfa_resp["AuthenticationResult"]["IdToken"]
            return id_token
        else:
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


def login_flow(config: dict) -> dict:
    """
    Full login flow: prompts for username/password, handles MFA, returns AWS credentials dict.
    """
    load_auth_config(config)
    username = input("Cognito username: ")
    import getpass
    password = getpass.getpass("Cognito password: ")
    id_token = cognito_login(username, password)
    creds = get_aws_credentials_from_cognito(id_token)
    print("[auth] Login successful. Temporary AWS credentials obtained.")
    return creds

# Example usage (to be called from CLI):
# id_token = cognito_login(username, password)
# creds = get_aws_credentials_from_cognito(id_token) 