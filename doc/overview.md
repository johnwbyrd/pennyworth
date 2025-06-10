# System Overview (Current State)

## Introduction
Pennyworth is a serverless, OpenAI-compatible API proxy for AWS Bedrock and other LLMs. All user and API key management is performed via Amazon Cognito and REST API endpoints—there is no DynamoDB or direct AWS SDK access for clients. The system is designed for secure, zero-cost-at-rest operation, with robust observability and modern CI/CD.

## Core Components and Responsibilities

### 1. API Gateway
- **Entry point** for all HTTP(S) requests from clients (OpenAI API, VS Code, Cursor, CLI, etc.)
- Routes requests to a single Lambda handler
- Handles CORS, throttling, and streaming

### 2. AWS Lambda (Unified Handler)
- **Single entry point** (`api.py`) using AWS Lambda Powertools for routing, logging, and tracing
- Modular handler pattern: all business logic is delegated to handler modules (OpenAI, MCP, users, etc.)
- Implements OpenAI-compatible and MCP endpoints
- Centralized authentication and authorization in `auth.py` (API key and Cognito JWT)
- Uses Cognito Identity Pool to assume user context for AWS operations
- All responses are formatted for API Gateway v1, with robust error handling and logging

### 3. Amazon Cognito
- **Single source of truth** for users and API keys (stored as custom attributes)
- All user and key management is via REST endpoints (no direct AWS SDK/DynamoDB access)
- Permissions and group membership managed via Cognito groups

### 4. CloudWatch & X-Ray
- Logging and metrics via Powertools Logger
- X-Ray tracing enabled for all Lambda entrypoints and handler methods
- Log retention set to 14 days

### 5. Clients
- CLI, VS Code, Cursor, and custom apps
- Authenticate via Cognito JWTs or API keys
- CLI is a pure REST client (no direct AWS access)

### 6. (Optional) S3
- For large file uploads if needed (not currently a core pattern)

## Request Flow
1. **Client** sends HTTP request (with JWT or API key) to API Gateway
2. **API Gateway** forwards to Lambda
3. **Lambda**:
   - Authenticates via `auth.py`
   - Attaches user-context boto3 session if needed
   - Routes to appropriate handler
   - Handler performs business logic, possibly using Cognito or other AWS services
   - Response is serialized and returned via API Gateway
   - All actions are logged and traced
4. **CloudWatch** and **X-Ray** capture logs and traces

## Security Model
- All authentication and authorization is centralized in `auth.py`
- API keys and user management are handled exclusively via Cognito and REST endpoints
- No plaintext API keys are stored or returned after creation
- Least-privilege IAM roles for Lambda and users

## Observability & Debugging
- Powertools Logger and Tracer used throughout
- X-Ray traces all Lambda entrypoints and handler methods
- Structured logging for all responses and errors
- Log retention and metrics configured via CI/CD

## CI/CD and Deployment
- GitHub Actions workflow deploys via AWS SAM
- Git commit SHA is passed as an environment variable and exposed in the `/v1/version` endpoint
- All configuration is via environment variables and SAM parameters

## Directory Structure
```
/
├── template.yaml                # SAM/CloudFormation template
├── README.md
├── LICENSE
├── requirements-dev.txt         # (Optional) Dev/test dependencies
├── .github/
│   └── workflows/
│       └── deploy.yml
├── doc/
│   └── ...                      # Documentation
├── src/
│   ├── lambda/
│   │   ├── api.py               # Lambda handler (entry point)
│   │   ├── requirements.txt     # Lambda dependencies
│   │   └── ...                  # Supporting modules/configs
│   └── cli/                     # CLI tool code
│       └── ...                  # CLI Python files
└── tests/
    └── ...                      # Unit/integration tests
```

- `src/lambda/`: All Lambda function code and dependencies. `api.py` is the entry point. Add `requirements.txt` here for Lambda dependencies.
- `src/cli/`: CLI tool for API key management and admin tasks (REST client only).
- `tests/`: For unit and integration tests.
- `requirements-dev.txt`: (Optional) For development and test dependencies (e.g., pytest, black).
- `template.yaml`: The main AWS SAM/CloudFormation template, referencing `src/lambda/` as the Lambda `CodeUri`.
- `.github/workflows/`: CI/CD pipeline definitions.
- `doc/`: Project documentation.

## Extensibility and Future Work
- Modular handler pattern supports easy addition of new endpoints
- MCP protocol support is now a core requirement, not optional
- CLI and admin tools are REST-only
- S3 integration for large payloads is available if needed

## Updated Summary Table
| Component   | Depends On         | Provides To         |
|-------------|--------------------|---------------------|
| API Gateway | Lambda, CloudWatch | Clients             |
| Lambda      | Cognito, CloudWatch, X-Ray | API Gateway      |
| Cognito     | -                  | Lambda              |
| CloudWatch  | -                  | API Gateway, Lambda |
| X-Ray       | -                  | Lambda              |
| Clients     | API Gateway        | -                   |
| S3 (opt.)   | -                  | Clients, Lambda     |

## Updated Diagram (Textual)
```
Clients ──> API Gateway ──> Lambda (Powertools Routing)
                        │                │
                        │                └──> Cognito (users, API keys)
                        │
                        └──> CloudWatch (logs/metrics)
                        │
                        └──> X-Ray (tracing)

[Optional: S3 for large file transfer]
```

---

This overview reflects the actual, current state of Pennyworth: a secure, serverless, OpenAI-compatible API proxy with all user and key management via Cognito and REST, robust observability, and modern CI/CD.

See the [README](../README.md) for details on environment variable naming and configuration conventions. 