# Makes src.shared.constants a Python package. 

import os
import time

PENNYWORTH_BASE_DOMAIN = os.environ.get('PENNYWORTH_BASE_DOMAIN', 'uproro.com')
"""
The base domain for the API (e.g., 'api.example.com').
Set by: Environment variable 'PENNYWORTH_BASE_DOMAIN'.
Used for: Constructing API URLs, custom domains.
"""

PENNYWORTH_API_URL = os.environ.get('PENNYWORTH_API_URL', f'https://api.{PENNYWORTH_BASE_DOMAIN}/v1')
"""
The full base URL for the API (e.g., 'https://api.example.com/v1').
Set by: Environment variable 'PENNYWORTH_API_URL'.
Used for: REST API requests from CLI and internal code.
"""

PENNYWORTH_USER_POOL_ID = os.environ.get('PENNYWORTH_USER_POOL_ID', 'PENNYWORTH_USER_POOL_ID_NOT_SET')
"""
Cognito User Pool ID for authentication.
Set by: Environment variable 'PENNYWORTH_USER_POOL_ID' (injected by template.yaml).
Used for: Cognito authentication, JWT validation.
"""

PENNYWORTH_USER_POOL_CLIENT_ID = os.environ.get('PENNYWORTH_USER_POOL_CLIENT_ID', 'PENNYWORTH_USER_POOL_CLIENT_ID_NOT_SET')
"""
Cognito User Pool Client ID for authentication.
Set by: Environment variable 'PENNYWORTH_USER_POOL_CLIENT_ID' (injected by template.yaml).
Used for: Cognito authentication, JWT validation.
"""

PENNYWORTH_IDENTITY_POOL_ID = os.environ.get('PENNYWORTH_IDENTITY_POOL_ID', 'PENNYWORTH_IDENTITY_POOL_ID_NOT_SET')
"""
Cognito Identity Pool ID for AWS credential exchange.
Set by: Environment variable 'PENNYWORTH_IDENTITY_POOL_ID' (injected by template.yaml).
Used for: Exchanging JWTs for AWS credentials.
"""

PENNYWORTH_AWS_REGION = os.environ.get('PENNYWORTH_AWS_REGION', 'PENNYWORTH_AWS_REGION_NOT_SET')
"""
AWS region for all AWS service calls.
Set by: Environment variable 'PENNYWORTH_AWS_REGION' (injected by template.yaml).
Used for: AWS SDK calls, Cognito, Lambda, etc.
"""

PENNYWORTH_API_VERSION = os.environ.get('PENNYWORTH_API_VERSION', 'PENNYWORTH_API_VERSION_NOT_SET')
"""
API version string (e.g., 'v1').
Set by: Environment variable 'PENNYWORTH_API_VERSION' (injected by template.yaml).
Used for: Routing, versioning endpoints.
"""

PENNYWORTH_API_SEMANTIC_VERSION = os.environ.get('PENNYWORTH_API_SEMANTIC_VERSION', 'PENNYWORTH_API_SEMANTIC_VERSION_NOT_SET')
"""
Semantic version string (e.g., '0.1.0').
Set by: Environment variable 'PENNYWORTH_API_SEMANTIC_VERSION' (injected by template.yaml).
Used for: Version reporting, diagnostics.
"""

PENNYWORTH_GIT_COMMIT = os.environ.get('PENNYWORTH_GIT_COMMIT', 'PENNYWORTH_GIT_COMMIT_NOT_SET')
"""
Git commit SHA for this deployment.
Set by: Environment variable 'PENNYWORTH_GIT_COMMIT' (injected by template.yaml).
Used for: Diagnostics, version reporting.
"""

PENNYWORTH_SESSION_DIR = os.environ.get('PENNYWORTH_SESSION_DIR', os.path.join(os.path.expanduser("~"), ".pennyworth"))
"""
Directory for storing CLI session files.
Set by: Environment variable 'PENNYWORTH_SESSION_DIR'.
Used for: CLI session persistence.
"""

PENNYWORTH_SESSION_FILE = os.environ.get('PENNYWORTH_SESSION_FILE', 'PENNYWORTH_SESSION_FILE_NOT_SET')
"""
Filename for CLI session file.
Set by: Environment variable 'PENNYWORTH_SESSION_FILE'.
Used for: CLI session persistence.
"""

PENNYWORTH_API_TIMEOUT = int(os.environ.get('PENNYWORTH_API_TIMEOUT', '15'))
"""
Timeout (in seconds) for API requests.
Set by: Environment variable 'PENNYWORTH_API_TIMEOUT'.
Used for: HTTP request timeouts in CLI and session code.
"""

PENNYWORTH_START_TIME = time.time()
"""
Timestamp when the process started (for debug/logging).
Set at runtime.
Used for: Debug logging, timing.
""" 