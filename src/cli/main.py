import os
import typer
from typing import Optional
import requests
import json
import boto3
import hashlib
import secrets
from .auth import login_flow

app = typer.Typer(help="Pennyworth API Key Management CLI.")

# Global config for stack and region
cli_config = {
    "api_url": f"https://api.{os.environ.get('BASE_DOMAIN', 'uproro.com')}",
}

# Global option to disable rich/fancy output
plain_output: bool = False

def _set_plain_output(plain: bool):
    """Disable color and rich formatting if --plain is set or NO_COLOR env var is present."""
    global plain_output
    plain_output = plain or os.environ.get("NO_COLOR") == "1"
    if plain_output:
        os.environ["CLICOLOR"] = "0"
        os.environ["NO_COLOR"] = "1"

# Fetch config from the well-known endpoint at startup
well_known_url = f"{cli_config['api_url']}/v1/parameters/well-known"
try:
    resp = requests.get(well_known_url, timeout=5)
    resp.raise_for_status()
    cognito_config = resp.json()
except Exception as e:
    raise RuntimeError(f"Failed to fetch Cognito config from {well_known_url}: {e}")

# ApiKeysTableName will be fetched after login from the protected endpoint
api_keys_table_name = None

def fetch_protected_config(id_token):
    protected_url = f"{cli_config['api_url']}/v1/parameters/protected"
    headers = {"Authorization": f"Bearer {id_token}"}
    resp = requests.get(protected_url, headers=headers, timeout=5)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise RuntimeError(f"Failed to fetch protected config: {resp.status_code} {resp.text}")

@app.callback()
def main(
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable color and rich formatting for output. Equivalent to setting NO_COLOR=1."
    ),
    stack: str = typer.Option(
        os.environ.get("PENNYWORTH_STACK_NAME", "pennyworth-prod"),
        "--stack",
        help="CloudFormation stack name (for display only)."
    ),
    region: str = typer.Option(
        cognito_config.get("Region", "us-west-2"),
        "--region",
        help="AWS region for the CLI config (for display only)."
    )
):
    """Pennyworth CLI entry point. Use --plain for minimal output. Use --stack and --region to select environment."""
    _set_plain_output(plain)
    cli_config["stack_name"] = stack
    cli_config["region"] = region

@app.command()
def create(
    owner: str = typer.Option(..., help="Owner/user/team identifier for the API key."),
    permissions: Optional[str] = typer.Option(None, help="Comma-separated permissions."),
    expiry: Optional[str] = typer.Option(None, help="Expiration date (ISO format)."),
    rate_limit: Optional[int] = typer.Option(None, help="Optional rate limit."),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json.")
):
    """Create a new API key."""
    creds = login_flow(cognito_config)
    id_token = creds.get("IdToken") or creds.get("id_token")
    if not id_token:
        raise RuntimeError("No ID token found in credentials.")
    protected = fetch_protected_config(id_token)
    api_keys_table_name = protected["ApiKeysTableName"]
    # Generate a random API key and hash
    api_key = secrets.token_urlsafe(32)
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    item = {
        "api_key_hash": {"S": api_key_hash},
        "owner": {"S": owner},
    }
    if permissions:
        item["permissions"] = {"S": permissions}
    if expiry:
        item["expiry"] = {"S": expiry}
    if rate_limit is not None:
        item["rate_limit"] = {"N": str(rate_limit)}
    # Write to DynamoDB
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretKey"],
        aws_session_token=creds["SessionToken"],
        region_name=cognito_config.get("region", "us-west-2"),
    )
    ddb = session.client("dynamodb")
    ddb.put_item(TableName=api_keys_table_name, Item=item)
    result = {
        "api_key": api_key,
        "api_key_hash": api_key_hash,
        "owner": owner,
        "permissions": permissions,
        "expiry": expiry,
        "rate_limit": rate_limit,
    }
    if output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"[create] API key created for owner '{owner}': {api_key}")
        print(f"[create] Hash: {api_key_hash}")
        if permissions:
            print(f"[create] Permissions: {permissions}")
        if expiry:
            print(f"[create] Expiry: {expiry}")
        if rate_limit is not None:
            print(f"[create] Rate limit: {rate_limit}")

@app.command()
def revoke(
    hash: str = typer.Option(..., help="API key hash to revoke."),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json.")
):
    """Revoke an existing API key by hash."""
    # TODO: Implement revoke logic
    if output == "json":
        print("{}")
    else:
        print("[revoke] (no-op)")

@app.command()
def audit(
    status: Optional[str] = typer.Option(None, help="Filter by key status (active, revoked, etc.)."),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json.")
):
    """Audit all API keys and their metadata."""
    creds = login_flow(cognito_config)
    # TODO: Implement audit logic using creds
    if output == "json":
        print(json.dumps({"aws_creds": creds}, indent=2))
    else:
        print("[audit] (no-op, creds obtained)")

@app.command()
def status(
    hash: str = typer.Option(..., help="API key hash to check status for."),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json.")
):
    """Check the status of a specific API key."""
    # TODO: Implement status logic
    if output == "json":
        print("{}")
    else:
        print("[status] (no-op)")

@app.command()
def rotate(
    hash: str = typer.Option(..., help="API key hash to rotate."),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json.")
):
    """Rotate an API key (revoke old, create new for same owner/permissions)."""
    # TODO: Implement rotate logic
    if output == "json":
        print("{}")
    else:
        print("[rotate] (no-op)")

if __name__ == "__main__":
    app() 