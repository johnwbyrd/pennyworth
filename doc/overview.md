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
  - Authenticates requests using API keys (by comparing secure hashes stored in DynamoDB)
  - Streams responses for long-running or large outputs
  - Handles error management and logging

### 3. DynamoDB (API Key Store)
- **Role:** Persistent, scalable storage for API key metadata and permissions
- **Security Note:** Only a secure hash (e.g., SHA-256) of each API key is stored—never the key itself. This ensures that even if the database is compromised, the actual keys remain secret.
- **Responsibilities:**
  - Stores API key hashes and their status (active, revoked, etc.)
  - Supports dynamic key management (add, revoke, rotate)
  - Optionally tracks usage, last used, and rate limits
  - Stores encrypted or hashed permissions if desired

### 4. CloudWatch
- **Role:** Observability and monitoring
- **Responsibilities:**
  - Collects logs from Lambda and API Gateway
  - Provides metrics for usage, errors, and performance
  - Supports alerting and dashboarding

### 5. Clients (VS Code, Cursor, Custom Apps)
- **Role:** Consumers of the OpenAI-compatible API
- **Responsibilities:**
  - Send requests to the API Gateway endpoint
  - Authenticate using API keys
  - Handle streaming and large responses as needed

### 6. (Optional) S3
- **Role:** Storage for large input files (if needed)
- **Responsibilities:**
  - Used when client inputs exceed API Gateway payload limits
  - Clients upload data to S3 and pass a reference in the API request

## High-Level Request Flow

1. **Client** sends an HTTP request (e.g., /v1/chat/completions) with an API key to the **API Gateway** endpoint.
2. **API Gateway** forwards the request to the **Lambda (LiteLLM)** function.
3. **Lambda**:
   - Hashes the presented API key and looks up the hash in **DynamoDB** (never stores or compares plaintext keys).
   - Checks permissions and status.
   - Routes the request to the appropriate LLM provider (e.g., Bedrock, OpenAI).
   - Streams the response back to the client via API Gateway.
   - Logs request/response details to **CloudWatch**.
4. If the request or response is too large, the client may use **S3** for data transfer (optional pattern).

## Interdependencies
- **API Gateway** depends on Lambda for compute and on CloudWatch for logging.
- **Lambda** depends on DynamoDB for API key validation, on LLM providers for model inference, and on CloudWatch for logging/metrics.
- **Clients** depend on API Gateway for access and on valid API keys in DynamoDB.
- **S3** is only used if large payloads are required.

## Summary Table
| Component   | Depends On         | Provides To         |
|-------------|--------------------|---------------------|
| API Gateway | Lambda, CloudWatch | Clients             |
| Lambda      | DynamoDB, LLMs, CloudWatch | API Gateway      |
| DynamoDB    | -                  | Lambda              |
| CloudWatch  | -                  | API Gateway, Lambda |
| Clients     | API Gateway        | -                   |
| S3 (opt.)   | -                  | Clients, Lambda     |

## Diagram (Textual)

```
Clients ──> API Gateway ──> Lambda (LiteLLM) ──> [Bedrock/OpenAI/etc.]
                        │                │
                        │                └──> DynamoDB (API key hashes)
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