import os
import typer
from typing import Optional
import requests
import json
from .auth import login_flow

app = typer.Typer(help="Pennyworth API Key Management CLI.")

# Global config for stack and region
cli_config = {
    "api_url": os.environ.get("PENNYWORTH_API_URL", "https://api.uproro.com"),
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
well_known_url = f"{cli_config['api_url']}/v1/well-known/parameters"
try:
    resp = requests.get(well_known_url, timeout=5)
    resp.raise_for_status()
    cognito_config = resp.json()
except Exception as e:
    raise RuntimeError(f"Failed to fetch Cognito config from {well_known_url}: {e}")

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
        cognito_config.get("region", "us-west-2"),
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
    # TODO: Implement key creation logic using creds
    if output == "json":
        print(json.dumps({"aws_creds": creds}, indent=2))
    else:
        print("[create] (no-op, creds obtained)")

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