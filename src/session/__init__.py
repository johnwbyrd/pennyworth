import os
import json
import getpass
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# Session storage configuration
SESSION_DIR = os.environ.get("PENNYWORTH_SESSION_DIR", os.path.join(os.path.expanduser("~"), ".pennyworth"))
SESSION_FILE = os.environ.get("PENNYWORTH_SESSION_FILE", "session.json")

# API configuration
API_URL = os.environ.get("PENNYWORTH_API_URL", "https://api.uproro.com")
API_TIMEOUT = int(os.environ.get("PENNYWORTH_API_TIMEOUT", "15"))  # seconds

START_TIME = time.time()

def log_debug(msg, verbose=False):
    if verbose:
        elapsed = time.time() - START_TIME
        print(f"[DEBUG +{elapsed:.2f}s] {msg}")

def get_session(params: Optional[dict] = None) -> Optional[Dict[str, Any]]:
    """
    Get a valid session by either:
    1. Using existing valid session from ~/.pennyworth/session.json
    2. Using provided credentials to create new session
    3. Prompting for credentials if needed
    Args:
        params: Optional dict with keys 'username', 'password', 'new_password', 'verbose'
    Returns:
        Dict containing session data (jwt_token, aws_credentials) or None if no valid session
    """
    verbose = params.get('verbose', False) if params else False
    username = params.get('username') if params else None
    password = params.get('password') if params else None
    new_password = params.get('new_password') if params else None
    # First check existing session
    t0 = time.time()
    log_debug("Loading existing session...", verbose)
    session = _load_session()
    t1 = time.time()
    if session:
        if not _is_session_expired(session):
            log_debug(f"Loaded session in {t1-t0:.2f}s (session found, valid)", verbose)
        else:
            log_debug(f"Loaded session in {t1-t0:.2f}s (session found, expired)", verbose)
    else:
        log_debug(f"Loaded session in {t1-t0:.2f}s (no session found)", verbose)
    if session and not _is_session_expired(session):
        log_debug("Session is valid.", verbose)
        return session
    
    # Need to authenticate
    if not username:
        username = input("Cognito username: ")
    if not password:
        password = getpass.getpass("Cognito password: ")
    
    try:
        # Get Cognito config
        t2 = time.time()
        log_debug("Fetching Cognito config...", verbose)
        config = _get_cognito_config()
        t3 = time.time()
        log_debug(f"Fetched Cognito config in {t3-t2:.2f}s", verbose)
        
        # Authenticate with Cognito
        t4 = time.time()
        log_debug("Authenticating with Cognito...", verbose)
        id_token = _authenticate_with_cognito(config, username, password, new_password)
        t5 = time.time()
        log_debug(f"Authenticated with Cognito in {t5-t4:.2f}s", verbose)
        
        # Get AWS credentials
        t6 = time.time()
        log_debug("Getting AWS credentials...", verbose)
        aws_creds = _get_aws_credentials(config, id_token)
        t7 = time.time()
        log_debug(f"Got AWS credentials in {t7-t6:.2f}s", verbose)
        
        # Create session
        session = {
            "jwt_token": id_token,
            "aws_credentials": aws_creds
        }
        
        # Save session
        t8 = time.time()
        log_debug("Saving session...", verbose)
        _save_session(session)
        t9 = time.time()
        log_debug(f"Saved session in {t9-t8:.2f}s", verbose)
        
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
        # Ensure aws_credentials["Expiration"] is a string
        session_copy = session.copy()
        if "aws_credentials" in session_copy and "Expiration" in session_copy["aws_credentials"]:
            exp = session_copy["aws_credentials"]["Expiration"]
            if hasattr(exp, 'isoformat'):
                session_copy["aws_credentials"] = session_copy["aws_credentials"].copy()
                session_copy["aws_credentials"]["Expiration"] = exp.isoformat()
        with open(session_file, "w") as f:
            json.dump(session_copy, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving session: {e}")

def _is_session_expired(session: Dict[str, Any]) -> bool:
    """Check if session is expired"""
    from datetime import datetime
    try:
        expires = datetime.fromisoformat(session["aws_credentials"]["Expiration"].replace("Z", "+00:00"))
        return datetime.now(expires.tzinfo) >= expires
    except Exception:
        return True

def _get_cognito_config() -> Dict[str, str]:
    """Get Cognito configuration from well-known endpoint"""
    well_known_url = f"{API_URL}/v1/parameters/well-known"
    
    try:
        resp = requests.get(well_known_url, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout after {API_TIMEOUT} seconds while fetching Cognito config from {well_known_url}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch Cognito config from {well_known_url}: {e}")

def _authenticate_with_cognito(config: Dict[str, str], username: str, password: str, new_password: Optional[str] = None) -> str:
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
                        if not new_password:
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
                            new_password = None  # Clear the failed password
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
    import argparse
    parser = argparse.ArgumentParser(description="Pennyworth session management")
    parser.add_argument("--username", help="Cognito username")
    parser.add_argument("--password", help="Cognito password")
    parser.add_argument("--new-password", help="New password (if change required)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()
    params = {k: v for k, v in vars(args).items() if k in ("username", "password", "new_password", "verbose") and v is not None}
    try:
        session = get_session(params)
        if session:
            print("Current session valid until:", session["aws_credentials"]["Expiration"])
            exit(0)
        else:
            print("No valid session")
            exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(2) 