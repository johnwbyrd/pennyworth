# Project Plan & Current State: Pennyworth

## Project Overview
Pennyworth is a serverless, OpenAI-compatible API proxy for AWS Bedrock (and other LLMs), designed for secure, zero-cost-at-rest operation. It leverages AWS Lambda, API Gateway, Cognito (as the single source of truth for users and API keys), and supporting AWS infrastructure, with a focus on least-privilege IAM, CI/CD automation, and maintainability. The project is licensed AGPL-3.0-only.

---

## Current State (as of latest refactor)

### Codebase & Architecture
- **Single Lambda Entrypoint:** All routing is handled in `src/lambda/api.py` using AWS Lambda Powertools' event handler decorators.
- **Modular Handlers:** All business logic is delegated to handler modules in `src/lambda/handlers/` (`openai.py`, `mcp.py`, `well_known.py`, `protected.py`).
- **Centralized Authentication:** All API key and Cognito JWT authentication is handled in `src/lambda/auth.py` with a strict, auditable, default-deny approach.
- **Logging & Tracing:** Uses AWS Lambda Powertools logger and tracer, instantiated in `src/lambda/utils.py` and imported where needed. X-Ray is enabled for all handlers.
- **Consistent Endpoint Versioning:** All endpoints are under `/v1` for future-proofing and clarity.
- **Environment Variables:** All configuration is via environment variables, with no secrets in code.
- See the [README](../README.md) for details on environment variable naming and configuration conventions.
- All project-specific environment variables are prefixed with `PENNYWORTH_` (e.g., `PENNYWORTH_BASE_DOMAIN`, `PENNYWORTH_API_URL`, etc.).
- All configuration constants are centralized in `src/shared/constants/__init__.py`.

### Infrastructure
- **API Gateway:** Routes all `/v1/*` traffic to the Lambda function.
- **Lambda:** Handles all OpenAI-compatible and MCP API requests, authenticates via API keys or Cognito JWTs, and proxies to Bedrock via LiteLLM.
- **Cognito:** Used as the single source of truth for all users and API keys. All user and key management, permissions, and status checks are centralized in Cognito via REST endpoints.
- **IAM:** All roles are least-privilege and tightly scoped, with role mappings based on Cognito groups.
- **CloudWatch & X-Ray:** All logs are collected and retained for 14 days. X-Ray traces all Lambda entrypoints and handler methods.

### Security
- **Centralized, auditable authentication** for all endpoints.
- **No plaintext API keys are stored or returned after creation.**
- **Least-privilege IAM** for Lambda and users.
- **All configuration is via environment variables and SAM parameters.**
- **No secrets in code.**

### CI/CD
- **GitHub Actions** is used for CI/CD, deploying via AWS SAM.
- The **Git commit SHA** is passed as an environment variable and exposed in the `/v1/version` endpoint.

### Directory Structure
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

### MCP Protocol
- **MCP protocol support is now a core requirement, not optional.**

---

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
