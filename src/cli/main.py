import os
import typer
from typing import Optional

app = typer.Typer(help="Pennyworth API Key Management CLI.")

# Global option to disable rich/fancy output
plain_output: bool = False

def _set_plain_output(plain: bool):
    """Disable color and rich formatting if --plain is set or NO_COLOR env var is present."""
    global plain_output
    plain_output = plain or os.environ.get("NO_COLOR") == "1"
    if plain_output:
        os.environ["CLICOLOR"] = "0"
        os.environ["NO_COLOR"] = "1"

@app.callback()
def main(
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Disable color and rich formatting for output. Equivalent to setting NO_COLOR=1."
    )
):
    """Pennyworth CLI entry point. Use --plain for minimal output."""
    _set_plain_output(plain)

@app.command()
def create(
    owner: str = typer.Option(..., help="Owner/user/team identifier for the API key."),
    permissions: Optional[str] = typer.Option(None, help="Comma-separated permissions."),
    expiry: Optional[str] = typer.Option(None, help="Expiration date (ISO format)."),
    rate_limit: Optional[int] = typer.Option(None, help="Optional rate limit."),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text or json.")
):
    """Create a new API key."""
    # TODO: Implement key creation logic
    if output == "json":
        print("{}")
    else:
        print("[create] (no-op)")

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
    # TODO: Implement audit logic
    if output == "json":
        print("[]")
    else:
        print("[audit] (no-op)")

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