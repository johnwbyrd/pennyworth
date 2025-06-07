# Project Plan & Current State: Pennyworth

## Project Overview
Pennyworth is a serverless, OpenAI-compatible API proxy for AWS Bedrock (and other LLMs), designed for secure, zero-cost-at-rest operation. It leverages AWS Lambda, API Gateway, DynamoDB, Cognito, and supporting AWS infrastructure, with a focus on least-privilege IAM, CI/CD automation, and maintainability. The project is licensed AGPL-3.0-only.

---

## Current State (as of latest refactor)

### Codebase & Architecture
- **Single Lambda Entrypoint:** All routing is handled in `src/lambda/api.py` using AWS Lambda Powertools' event handler decorators.
- **Modular Handlers:** All business logic is delegated to handler modules in `src/lambda/handlers/` (`openai.py`, `mcp.py`, `well_known.py`, `protected.py`).
- **Centralized Authentication:** All API key and Cognito JWT authentication is handled in `src/lambda/auth.py` with a strict, auditable, default-deny approach.
- **Logging:** Uses AWS Lambda Powertools logger, instantiated in `src/lambda/utils.py` and imported where needed.
- **Obsolete Files Removed:** Old handler and utility files have been deleted for clarity and maintainability.
- **Consistent Endpoint Versioning:** All endpoints are under `/v1` for future-proofing and clarity.
- **Environment Variables:** All configuration is via environment variables, with no secrets in code.

### Infrastructure
- **API Gateway:** Routes all `/v1/*` traffic to the Lambda function.
- **Lambda:** Handles all OpenAI-compatible and MCP API requests, authenticates via API keys, and proxies to Bedrock via LiteLLM.
- **DynamoDB:** Stores API key hashes and metadata.
- **Cognito:** Used for CLI/admin authentication and JWT validation.
- **IAM:** All roles are least-privilege and tightly scoped.
- **CloudWatch:** All logs are collected and retained for 14 days.

### Security
- **Centralized, auditable authentication** for all endpoints.
- **No plaintext API keys** are stored or logged.
- **No static AWS credentials**; all access is via IAM roles and OIDC.

### What is Working
- End-to-end deployment and infrastructure provisioning via CI/CD.
- Modular, maintainable Lambda codebase with clear separation of concerns.
- API Gateway and Lambda are live and reachable at the custom domain.
- API key management is functional (DynamoDB, CLI IAM role).
- Logging and error handling are robust and centralized.
- Documentation is up to date and in-repo.

---

## Next Steps / Detailed Plan

### 1. **Implement Real API Key Validation**
- Implement DynamoDB lookup and hash validation in `require_api_key_auth` in `auth.py`.
- Add usage tracking (calls, last used) per API key.
- Add error responses and logging for invalid/expired keys.

### 2. **Enable LLM Responses via LiteLLM in Lambda**
- Ensure all LiteLLM and Bedrock dependencies are included in the Lambda deployment package.
- Test and debug end-to-end LLM proxying (OpenAI endpoints to Bedrock via LiteLLM).
- Add error handling and logging for failed LLM invocations.
- Support additional OpenAI endpoints as needed.

### 3. **CLI Tooling and API Key Management**
- Expand CLI for API key creation, revocation, rotation, and audit.
- Integrate CLI authentication with Cognito and temporary AWS credentials.
- Add tests and usage examples for the CLI.

### 4. **Security & IAM Hardening**
- Review and restrict IAM policies (remove wildcards where possible).
- Enforce MFA for all admin/CLI users in Cognito.
- Set up alerts for failed authentication attempts or permission errors.

### 5. **Monitoring, Logging, and Observability**
- Add custom CloudWatch metrics and alarms for Lambda invocations, errors, and latency.
- Create CloudWatch dashboards for operational visibility.
- Ensure logs never contain full API keys or sensitive data.

### 6. **Cost Tracking & Reporting**
- Store usage and cost data in DynamoDB, keyed by API key or user.
- Publish cost metrics to CloudWatch for alerting and reporting.
- Plan for future dashboards or automated cost reports.

### 7. **Documentation & Onboarding**
- Update and expand documentation for environment variables, secrets, and configuration.
- Provide onboarding guide and architecture diagrams.
- Ensure CLI and API endpoints are fully documented with examples.

### 8. **Future Enhancements**
- Plan for a web-based admin UI for API key and usage management.
- Integrate with billing/analytics platforms for deeper insights.
- Add support for bulk key operations and notification integrations.
- Add support for more granular, per-key or per-user permissions if needed.

---

## Key Principles
- **Security:** OIDC for CI/CD, hashed API keys, least-privilege IAM, no plaintext secrets.
- **Configurability:** All deployment/runtime config via variables/secrets.
- **Cost Awareness:** Track/report per-user Bedrock costs as a core feature.
- **Maintainability:** Modular code, clear docs, automated tests, and CI/CD.

---

**Next milestone:**
> Successfully return a real LLM response from the deployed API, via LiteLLM proxying to Bedrock, using the OpenAI-compatible or MCP API.

This document reflects the current state and priorities for Pennyworth, and is suitable for handoff or further discussion in a new context. 