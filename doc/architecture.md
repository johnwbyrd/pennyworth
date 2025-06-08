# Architecture Overview (Current State)

## Purpose
Pennyworth is a serverless, OpenAI-compatible API proxy for AWS Bedrock and other LLMs. All user and API key management is performed via Amazon Cognito and REST API endpoints—there is no DynamoDB or LiteLLM built-in key management. The system is designed for secure, zero-cost-at-rest operation, robust observability, and modern CI/CD.

## High-Level Architecture

- **API Gateway**: Entry point for all HTTP(S) requests from clients (OpenAI API, MCP protocol, CLI, etc.). Routes to a single Lambda handler, handles CORS, throttling, and streaming.
- **AWS Lambda (Unified Handler)**: Single entry point (`api.py`) using AWS Lambda Powertools for routing, logging, and tracing. Modular handler pattern for business logic (OpenAI, MCP, users, etc.). Implements OpenAI-compatible and MCP endpoints. Centralized authentication and authorization in `auth.py`. Uses Cognito Identity Pool for user-context AWS operations. Robust error handling and response formatting.
- **Amazon Cognito**: Single source of truth for users and API keys (stored as custom attributes). All user and key management is via REST endpoints. Permissions and group membership managed via Cognito groups.
- **CloudWatch & X-Ray**: Logging and metrics via Powertools Logger. X-Ray tracing for all handlers and middleware. Log retention set via CI/CD.
- **Clients**: CLI, VS Code, Cursor, and custom apps. Authenticate via Cognito JWTs or API keys. CLI is a pure REST client.
- **(Optional) S3**: For large file uploads if needed (not currently a core pattern).

## Key Design Principles
- **OpenAI API Compatibility**: All endpoints and request/response formats match OpenAI's API, enabling drop-in use with existing clients.
- **Multi-LLM Support**: Modular handler pattern supports AWS Bedrock, OpenAI, and other providers.
- **Serverless/Zero-Cost-At-Rest**: No compute costs when idle; all resources are on-demand.
- **Centralized, Auditable Auth**: All authentication and authorization is handled in `auth.py` using Cognito and REST endpoints only.
- **Modern CI/CD**: GitHub Actions workflow deploys via AWS SAM, passing the Git commit SHA as an environment variable and exposing it in the `/v1/version` endpoint. All configuration is via environment variables and SAM parameters.

## Handling Long-Running and Large Requests
- **Lambda Constraints**: Max execution time 15 minutes, max payload size 6 MB (synchronous), 256 KB (event payload), streaming supported.
- **Streaming Responses**: For chat/completions and other endpoints, Lambda response streaming is used to send partial results as they are generated.
- **S3 Integration**: For large payloads, clients may upload data to S3 and pass a reference in the API request (optional pattern).
- **Graceful Error Handling**: If a request risks exceeding Lambda's timeout or payload limits, the API returns a partial result or a clear error message.

## Security Model
- All authentication and authorization is centralized in `auth.py`.
- API keys and user management are handled exclusively via Cognito and REST endpoints.
- No plaintext API keys are stored or returned after creation.
- Least-privilege IAM roles for Lambda and users.

## Observability & Debugging
- Powertools Logger and Tracer used throughout.
- X-Ray traces all Lambda entrypoints and handler methods.
- Structured logging for all responses and errors.
- Log retention and metrics configured via CI/CD.

## Extensibility and Optional Extensions
- Modular handler pattern supports easy addition of new endpoints.
- MCP protocol support is now a core requirement, not optional.
- S3 integration for large payloads is available if needed.
- Custom usage tracking via CloudWatch or other stores.

## Summary Diagram
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

This architecture is designed to be robust, cost-effective, and easy to maintain, while supporting advanced use cases for developer productivity tools. All key management is performed via REST API endpoints and Cognito, with no DynamoDB or LiteLLM built-in key management. The CLI is a pure REST client and never stores or displays plaintext API keys after creation. 