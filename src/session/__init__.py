import os
import json
import getpass
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
import requests

# Session storage configuration
SESSION_DIR = os.environ.get("PENNYWORTH_SESSION_DIR", os.path.join(os.path.expanduser("~"), ".pennyworth"))
SESSION_FILE = os.environ.get("PENNYWORTH_SESSION_FILE", "session.json")

def get_session(username: Optional[str] = None, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a valid session by either:
    1. Using existing valid session from ~/.pennyworth/session.json
    2. Using provided credentials to create new session
    3. Prompting for credentials if needed
    
    Returns:
        Dict containing session data (jwt_token, aws_credentials, session_expires) or None if no valid session
    """
    # First check existing session
    session = _load_session()
    if session and not _is_session_expired(session):
        return session
        
    # Need to authenticate
    if not username:
        username = input("Cognito username: ")
    if not password:
        password = getpass.getpass("Cognito password: ")
        
    try:
        # Get Cognito config
        config = _get_cognito_config()
        
        # Authenticate with Cognito
        id_token = _authenticate_with_cognito(config, username, password)
        
        # Get AWS credentials
        aws_creds = _get_aws_credentials(config, id_token)
        
        # Create session
        session = {
            "jwt_token": id_token,
            "aws_credentials": aws_creds,
            "session_expires": aws_creds["Expiration"]
        }
        
        # Save session
        _save_session(session)
        
        return session
        
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def _load_session() -> Optional[Dict[str, Any]]:
    """Load session from ~/.pennyworth/session.json"""
    session_file = os.path.join(SESSION_DIR, SESSION_FILE)
    try:
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading session: {e}")
    return None

def _save_session(session: Dict[str, Any]) -> None:
    """Save session to ~/.pennyworth/session.json"""
    session_file = os.path.join(SESSION_DIR, SESSION_FILE)
    
    try:
        os.makedirs(SESSION_DIR, exist_ok=True)
        with open(session_file, "w") as f:
            json.dump(session, f, indent=2)
    except Exception as e:
        print(f"Error saving session: {e}")

def _is_session_expired(session: Dict[str, Any]) -> bool:
    """Check if session is expired"""
    from datetime import datetime
    try:
        expires = datetime.fromisoformat(session["session_expires"].replace("Z", "+00:00"))
        return datetime.now(expires.tzinfo) >= expires
    except Exception:
        return True

def _get_cognito_config() -> Dict[str, str]:
    """Get Cognito configuration from well-known endpoint"""
    api_url = os.environ.get("PENNYWORTH_API_URL", "https://api.uproro.com")
    well_known_url = f"{api_url}/v1/parameters/well-known"
    
    try:
        resp = requests.get(well_known_url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Cognito config: {e}")

def _authenticate_with_cognito(config: Dict[str, str], username: str, password: str) -> str:
    """Authenticate with Cognito and handle challenges (MFA, password change)"""
    client = boto3.client("cognito-idp", region_name=config.get("Region", "us-west-2"))
    
    try:
        resp = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=config["UserPoolClientId"],
        )
        
        # Handle challenges
        while "ChallengeName" in resp:
            if resp["ChallengeName"] == "NEW_PASSWORD_REQUIRED":
                # Allow up to 3 attempts for password change
                for attempt in range(3):
                    try:
                        new_password = getpass.getpass("New password required. Enter new password: ")
                        resp = client.respond_to_auth_challenge(
                            ClientId=config["UserPoolClientId"],
                            ChallengeName="NEW_PASSWORD_REQUIRED",
                            Session=resp["Session"],
                            ChallengeResponses={
                                "USERNAME": username,
                                "NEW_PASSWORD": new_password,
                            },
                        )
                        # If we get here, password change was successful
                        break
                    except ClientError as e:
                        if attempt < 2:  # Don't print error on last attempt
                            print(f"Password change failed: {e}")
                            print("Please try again.")
                        else:
                            raise RuntimeError(f"Failed to set new password after 3 attempts: {e}")
            elif resp["ChallengeName"] in ("SMS_MFA", "SOFTWARE_TOKEN_MFA"):
                # Allow up to 3 attempts for MFA
                for attempt in range(3):
                    try:
                        mfa_code = input(f"Enter MFA code ({resp['ChallengeName']}): ")
                        resp = client.respond_to_auth_challenge(
                            ClientId=config["UserPoolClientId"],
                            ChallengeName=resp["ChallengeName"],
                            Session=resp["Session"],
                            ChallengeResponses={
                                "USERNAME": username,
                                ("SMS_MFA_CODE" if resp["ChallengeName"] == "SMS_MFA" else "SOFTWARE_TOKEN_MFA_CODE"): mfa_code,
                            },
                        )
                        # If we get here, MFA was successful
                        break
                    except ClientError as e:
                        if attempt < 2:  # Don't print error on last attempt
                            print(f"MFA verification failed: {e}")
                            print("Please try again.")
                        else:
                            raise RuntimeError(f"Failed MFA verification after 3 attempts: {e}")
            else:
                raise RuntimeError(f"Unsupported Cognito challenge: {resp['ChallengeName']}")
                
        if "AuthenticationResult" in resp:
            return resp["AuthenticationResult"]["IdToken"]
        else:
            raise RuntimeError("Unexpected Cognito response")
            
    except ClientError as e:
        raise RuntimeError(f"Authentication failed: {e}")

def _get_aws_credentials(config: Dict[str, str], id_token: str) -> Dict[str, str]:
    """Exchange Cognito JWT for AWS credentials"""
    cognito_identity = boto3.client("cognito-identity", region_name=config.get("Region", "us-west-2"))
    
    try:
        resp = cognito_identity.get_id(
            IdentityPoolId=config["IdentityPoolId"],
            Logins={f'cognito-idp.{config["Region"]}.amazonaws.com/{config["UserPoolId"]}': id_token}
        )
        identity_id = resp["IdentityId"]
        
        creds_resp = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={f'cognito-idp.{config["Region"]}.amazonaws.com/{config["UserPoolId"]}': id_token}
        )
        
        return creds_resp["Credentials"]
        
    except ClientError as e:
        raise RuntimeError(f"Failed to get AWS credentials: {e}")

if __name__ == "__main__":
    # When run directly, print current session or error
    try:
        session = get_session()
        if session:
            print("Current session valid until:", session["session_expires"])
            exit(0)
        else:
            print("No valid session")
            exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(2) 