# Pennyworth API Key Management CLI

A Python command-line tool for secure management of API keys in the Pennyworth system, using REST API endpoints as the backend. This tool never stores or displays plaintext API keys—only their hashes, and only shows the key once at creation.

## Features
- Create new API keys (secure, random, shown only once)
- Revoke existing API keys
- Audit all API keys and their metadata
- Check the status of a specific API key or system summary
- Output in human-friendly text or JSON
- Secure, scriptable, and suitable for production use

## Security Principles
- **No plaintext API keys are ever stored or displayed after creation.**
- **API keys are managed via REST API endpoints and stored as Cognito custom attributes.**
- **All REST API access is authenticated using Cognito JWTs.**
- **All output (except errors) is to stdout for easy redirection.**

## Requirements
- Python 3.8+
- requests (HTTP client)
- Typer (CLI framework)

## Command Structure

```
pennyworth-cli <command> [options]
```

### Commands

#### `create`
Create a new API key for a user/owner.
- **Arguments:**
  - `--owner <string>`: Owner/user/team identifier (required)
  - `--permissions <list>`: Comma-separated permissions (optional)
  - `--expiry <date>`: Expiration date (optional, ISO format)
  - `--rate-limit <int>`: Optional rate limit
  - `--output <format>`: `json` or `text` (default: `text`)
- **Behavior:**
  - Generates a secure random API key (256 bits, base64 or hex)
  - Sends a request to the REST API to create the key
  - Displays the plaintext key **once** to the user
- **Example:**
  ```bash
  pennyworth-cli create --owner alice --permissions read,write --expiry 2024-09-01 --output text
  ```
  Output:
  ```
  API Key (save this now, it will not be shown again):
  2f8c1e... (full key)
  Hash stored: abcd1234...
  Owner:      alice
  Permissions: read,write
  Expiry:     2024-09-01
  ```

#### `revoke`
Revoke an existing API key by hash or owner.
- **Arguments:**
  - `--hash <string>`: API key hash (required if --owner not given)
  - `--owner <string>`: Owner (optional, will revoke all keys for owner)
  - `--output <format>`: `json` or `text` (default: `text`)
- **Behavior:**
  - Sends a request to the REST API to revoke the key(s)
- **Example:**
  ```bash
  pennyworth-cli revoke --hash abcd1234... --output json
  ```

#### `audit`
List all API keys and their metadata.
- **Arguments:**
  - `--output <format>`: `json` or `text` (default: `text`)
  - `--owner <string>`: Filter by owner (optional)
  - `--status <string>`: Filter by status (active, revoked, expired; optional)
- **Behavior:**
  - Lists all keys (by hash), with metadata: owner, status, created_at, last_used, usage, permissions, expiry
  - Data is fetched from the REST API
- **Example:**
  ```bash
  pennyworth-cli audit --output text
  ```
  Output:
  ```
  Hash: abcd1234...  Owner: alice  Status: active  Created: 2024-06-01  Last Used: 2024-06-10  Usage: 42  Permissions: read,write  Expiry: 2024-09-01
  ...
  ```

#### `status`
Show the status of a specific API key or a summary of all keys.
- **Arguments:**
  - `--hash <string>`: API key hash (optional)
  - `--owner <string>`: Owner (optional)
  - `--output <format>`: `json` or `text` (default: `text`)
- **Behavior:**
  - If hash or owner is given, shows metadata for that key/owner
  - If neither is given, shows summary counts (total, active, revoked, expired)
  - Data is fetched from the REST API
- **Example:**
  ```bash
  pennyworth-cli status --hash abcd1234... --output json
  ```
  Output:
  ```json
  {
    "api_key_hash": "abcd1234...",
    "owner": "alice",
    "status": "active",
    "created_at": "2024-06-01T12:00:00Z",
    "last_used": "2024-06-10T09:00:00Z",
    "usage": 42,
    "permissions": ["read", "write"],
    "expiry": "2024-09-01"
  }
  ```

#### `rotate`
Rotate (replace) an API key for a user/owner.
- **Arguments:**
  - `--hash <string>`: API key hash to rotate (required)
  - `--output <format>`: `json` or `text` (default: `text`)
- **Behavior:**
  - Sends a request to the REST API to rotate the key
  - Displays the new key once
- **Example:**
  ```bash
  pennyworth-cli rotate --hash abcd1234... --output text
  ```

## Output Formats
- `--output text` (default): Human-friendly, columnar or labeled output
- `--output json`: Machine-readable JSON
- All output is to stdout (can be redirected to a file)
- Errors and warnings go to stderr

## Authentication
- Uses Cognito for authentication
- CLI obtains a JWT and uses it as a Bearer token for all REST API requests

## Usage Examples
```bash
# Create a new key for alice
pennyworth-cli create --owner alice --permissions read,write --output text

# Revoke a key by hash
pennyworth-cli revoke --hash abcd1234...

# Audit all active keys in JSON
pennyworth-cli audit --status active --output json > audit.json

# Check status of a specific key
pennyworth-cli status --hash abcd1234... --output text

# Rotate a key
pennyworth-cli rotate --hash abcd1234... --output text
```

## Security Notes
- Never share or store the plaintext API key after creation.
- API keys are managed as Cognito custom attributes and only shown to the user once.
- Use IAM permissions to restrict REST API access to authorized admins.
- All actions should be logged (optionally, to CloudWatch or a file) for audit purposes.

## Installation & Distribution
- Install via pip: `pip install pennyworth-cli` (planned)
- Or run as a standalone Python script

## Future Enhancements
- Bulk key creation/import/export
- Integration with notification systems (email, Slack)
- More granular permission management
- Additional output formats (CSV, YAML)

## Development Setup

To develop or run the Pennyworth CLI tool locally, follow these steps:

1. **Create and activate a Python virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```
   This will install Typer, requests, and any other dev/test tools needed for the CLI and project development.

3. **Run the CLI tool:**
   ```bash
   python src/cli/main.py --help
   ```

4. **(Optional) Deactivate the virtual environment when done:**
   ```bash
   deactivate
   ```

---

For more information on CLI usage and options, see the rest of this document.

For questions or contributions, see the project documentation or contact the maintainers.

## Configuration

See the [README](../README.md) for details on environment variable naming and configuration conventions. 