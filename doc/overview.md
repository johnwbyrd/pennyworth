# System Overview

## Components and Their Roles

### 1. API Gateway
- **Role:** Entry point for all HTTP(S) requests from clients (OpenAI API, VS Code, Cursor, etc.)
- **Responsibilities:**
  - Routes requests to the Lambda function
  - Handles CORS, throttling, and payload size limits
  - Supports Lambda response streaming for long-running outputs

### 2. AWS Lambda (LiteLLM)
- **Role:** Core compute layer running the LiteLLM proxy
- **Responsibilities:**
  - Implements OpenAI-compatible API endpoints
  - Routes requests to the appropriate LLM provider (Bedrock, OpenAI, etc.)
  - Authenticates requests using API keys (by looking up Cognito custom attributes)
  - Streams responses for long-running or large outputs
  - Handles error management and logging

### 3. Cognito (User and API Key Store)
- **Role:** Single source of truth for users and API keys
- **Security Note:** API keys are stored as custom attributes (e.g., `custom:api_key`) on Cognito users—never the key itself after creation. This ensures that even if the user directory is compromised, the actual keys remain secret.
- **API key management is exclusively handled via REST API endpoints; the CLI is a REST client.**
- **Responsibilities:**
  - Stores API key attributes and their status (active, revoked, etc.)
  - Supports dynamic key management (add, revoke, rotate) via REST endpoints
  - Optionally tracks usage, last used, and rate limits
  - Stores permissions as Cognito attributes if desired

### 4. CloudWatch
- **Role:** Observability and monitoring
- **Responsibilities:**
  - Collects logs from Lambda and API Gateway
  - Provides metrics for usage, errors, and performance
  - Supports alerting and dashboarding

### 5. Clients (VS Code, Cursor, Custom Apps, CLI)
- **Role:** Consumers of the OpenAI-compatible API
- **Responsibilities:**
  - Send requests to the API Gateway endpoint
  - Authenticate using API keys
  - Handle streaming and large responses as needed
  - **MCP protocol support is a near-term requirement for compatibility with VS Code, Cursor, and similar tools.**
  - CLI operates only via REST API endpoints, not direct AWS access

### 6. (Optional) S3
- **Role:** Storage for large input files (if needed)
- **Responsibilities:**
  - Used when client inputs exceed API Gateway payload limits
  - Clients upload data to S3 and pass a reference in the API request

## High-Level Request Flow

1. **Client** sends an HTTP request (e.g., /v1/chat/completions) with an API key to the **API Gateway** endpoint.
2. **API Gateway** forwards the request to the **Lambda (LiteLLM)** function.
3. **Lambda**:
   - Looks up the presented API key in Cognito custom attributes (never stores or compares plaintext keys after creation).
   - Checks permissions and status.
   - Routes the request to the appropriate LLM provider (e.g., Bedrock, OpenAI).
   - Streams the response back to the client via API Gateway.
   - Logs request/response details to **CloudWatch**.
4. If the request or response is too large, the client may use **S3** for data transfer (optional pattern).

## Interdependencies
- **API Gateway** depends on Lambda for compute and on CloudWatch for logging.
- **Lambda** depends on Cognito for API key validation, on LLM providers for model inference, and on CloudWatch for logging/metrics.
- **Clients** depend on API Gateway for access and on valid API keys in Cognito.
- **S3** is only used if large payloads are required.

## Summary Table
| Component   | Depends On         | Provides To         |
|-------------|--------------------|---------------------|
| API Gateway | Lambda, CloudWatch | Clients             |
| Lambda      | Cognito, LLMs, CloudWatch | API Gateway      |
| Cognito     | -                  | Lambda              |
| CloudWatch  | -                  | API Gateway, Lambda |
| Clients     | API Gateway        | -                   |
| S3 (opt.)   | -                  | Clients, Lambda     |

## Diagram (Textual)

```
Clients ──> API Gateway ──> Lambda (LiteLLM) ──> [Bedrock/OpenAI/etc.]
                        │                │
                        │                └──> Cognito (API key attributes)
                        │
                        └──> CloudWatch (logs/metrics)

[Optional: S3 for large file transfer]
```

---

## Debugging and Monitoring

- **CloudWatch Logs:** All Lambda logs (including print/console.log statements, errors, stack traces) are available in AWS Console → CloudWatch → Logs → Log groups (look for `/aws/lambda/<function-name>`).
- **CloudWatch Metrics:** View Lambda invocations, errors, duration, and custom metrics in CloudWatch → Metrics → Lambda.
- **X-Ray Tracing (optional):** Enable X-Ray in Lambda and API Gateway for end-to-end request tracing and performance analysis.
- **Local Debugging:** Use `sam local invoke` or `sam local start-api` to run and debug your Lambda locally with sample events and environment variables.
- **Lambda Console:** The "Monitor" tab shows recent invocations, errors, and links to logs.

**Best Practices:**
- Log all errors and key events with enough context (request ID, input, stack trace).
- Use structured logging (JSON) for easier searching and filtering.
- Set log retention to a reasonable period (e.g., 7 days) to control costs.

---

This overview captures the main moving pieces, their responsibilities, and how they interact to provide a secure, scalable, and OpenAI-compatible API proxy for modern developer tools. API key security is maintained by never storing plaintext keys on the server or in the database.

## Optional Extensions
- **MCP Protocol Support:** If required, a thin Lambda or container can be added to handle MCP endpoints and route to LiteLLM or directly to LLMs. **(Note: MCP support is now a near-term requirement, not just optional.)**

---

## Project Directory Structure

The following directory structure is recommended for maintainability, clarity, and scalability:

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
│   │   ├── app.py               # Lambda handler (entry point)
│   │   ├── requirements.txt     # Lambda dependencies (LiteLLM, etc.)
│   │   └── ...                  # Supporting modules/configs
│   └── cli/                     # CLI tool code
│       └── ...                  # CLI Python files
└── tests/
    └── ...                      # Unit/integration tests
```

**Directory and File Explanations:**
- `src/lambda/`: All Lambda function code and dependencies. `app.py` is the entry point. Add `requirements.txt` here for Lambda dependencies.
- `src/cli/`: CLI tool for API key management and admin tasks (now a REST client).
- `tests/`: For unit and integration tests.
- `requirements-dev.txt`: (Optional) For development and test dependencies (e.g., pytest, black).
- `template.yaml`: The main AWS SAM/CloudFormation template, referencing `src/lambda/` as the Lambda `CodeUri`.
- `.github/workflows/`: CI/CD pipeline definitions.
- `doc/`: Project documentation.

This structure supports local development, CI/CD, and future expansion (CLI, tests, multiple Lambdas, etc.). 