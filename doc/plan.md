# Project Plan & Current State: Pennyworth

## Project Overview
Pennyworth is a serverless, OpenAI-compatible API proxy for AWS Bedrock (or other LLMs), designed for secure, zero-cost-at-rest operation. It leverages AWS Lambda, API Gateway, DynamoDB, Cognito, and supporting AWS infrastructure, with a focus on least-privilege IAM, CI/CD automation, and maintainability. The project is licensed AGPL-3.0-only.

---

## Current State (as of latest deployment)

### Infrastructure
- **API Gateway**: Serves as the HTTP(S) entry point, routing requests to Lambda. Custom domain (e.g., `api.example.com`) is configured and live via Route 53 and ACM.
- **Lambda (LiteLLMProxyFunction)**: Main compute layer, running a LiteLLM-based proxy. Handles OpenAI-compatible and MCP API requests, authenticates via API keys, and routes to Bedrock. Permissions are tightly scoped: can access only DynamoDB (API keys table) and Bedrock (InvokeModel), with no access to Route 53, S3, or other AWS services.
- **Lambda (WellKnownParametersFunction)**: Serves public/protected endpoints for client configuration discovery. Minimal permissions (CloudWatch logging only).
- **DynamoDB**: Stores API key hashes and metadata. Point-in-time recovery and encryption enabled. Access is restricted to Lambda and CLI IAM roles.
- **Cognito User Pool & Client**: Manages CLI/admin user authentication. Enforces strong password policy and email verification.
- **Cognito Identity Pool**: Issues temporary AWS credentials to authenticated users, mapped to a dedicated IAM role.
- **IAM Roles**: All roles are least-privilege. Lambda and CLI roles are tightly scoped to only required resources/actions.
- **Route 53 & ACM**: Custom domain and certificate management are automated and integrated.
- **CloudWatch**: All Lambda/API Gateway logs are collected. Log retention is set to 14 days via automation.

### Security
- **IAM**: All Lambda and CLI roles are least-privilege. No wildcards except where required (e.g., Bedrock InvokeModel). No Route 53, S3, or other service access for Lambda.
- **API Keys**: Only secure hashes are stored in DynamoDB. No plaintext keys are ever logged or stored.
- **CI/CD**: GitHub Actions uses OIDC to assume a tightly-scoped deploy role. No static AWS keys are used.
- **Environment Variables**: All secrets/config are passed via environment variables or GitHub secrets.
- **MFA**: Supported for admin/CLI users via Cognito.

### Deployment & Automation
- **AWS SAM**: All infrastructure is defined as code in `template.yaml` and deployed via SAM.
- **GitHub Actions**: Automated build, deploy, and log retention. All parameters and secrets are managed via repository secrets.
- **Outputs**: All key resource IDs/ARNs are exported for CLI and integration use.

### What is Working
- End-to-end deployment: All infrastructure provisions cleanly via CI/CD.
- API Gateway and Lambda are live and reachable at the custom domain.
- API key management is functional via DynamoDB and CLI IAM role.
- Log retention and tagging are automated.
- Documentation is up to date and in-repo.

---

## Next Steps / Detailed Plan

### 1. **Enable LLM Responses via LiteLLM in Lambda**
- **Package LiteLLM and Dependencies:**
  - Ensure all LiteLLM dependencies (including Bedrock SDK, any required Python packages) are included in the Lambda deployment package.
  - Use a Lambda layer or Docker-based build if dependencies are large or require native binaries.
- **Configure LiteLLM for Bedrock:**
  - Set environment variables for Bedrock credentials, region, and model selection.
  - Update the Lambda handler to route OpenAI/MCP API requests to LiteLLM, and from there to Bedrock.
  - Add error handling and logging for failed LLM invocations.
- **Test End-to-End:**
  - Use curl, Postman, or an OpenAI-compatible client to send requests to the deployed endpoint.
  - Confirm that a real LLM response is returned from Bedrock via LiteLLM.
  - Debug and iterate on Lambda code and API Gateway integration as needed.
- **Support for Multiple Providers (Optional):**
  - If supporting more than Bedrock, add provider selection logic and configuration.

### 2. **Expand and Harden API Key Management**
- **CLI Tool:**
  - Implement and document CLI commands for API key creation, revocation, rotation, and audit.
  - Integrate CLI authentication with Cognito and ensure it uses temporary AWS credentials from the Identity Pool.
  - Add tests and usage examples for the CLI.
- **API Key Usage Tracking:**
  - Add logic to track per-key usage and last-used timestamps in DynamoDB.
  - Optionally, implement rate limiting or quotas per key.

### 3. **Security & IAM Hardening**
- **Review and Restrict IAM Policies:**
  - Remove any remaining wildcards from IAM policies (except where strictly necessary, e.g., Bedrock InvokeModel).
  - Restrict `iam:PassRole` to only the ARNs of Lambda and CLI roles created by the stack.
  - Enable and enforce MFA for all admin/CLI users in Cognito.
- **Audit and Monitoring:**
  - Regularly review IAM roles and CloudTrail logs for suspicious activity.
  - Set up alerts for failed authentication attempts or permission errors.

### 4. **Monitoring, Logging, and Observability**
- **CloudWatch Metrics and Alarms:**
  - Add custom metrics for Lambda invocations, errors, and latency.
  - Set up alarms for error rates, cost spikes, and unusual traffic patterns.
- **Dashboards:**
  - Create CloudWatch dashboards for operational visibility (API usage, error rates, cost tracking).
- **Log Redaction:**
  - Ensure that logs never contain full API keys or sensitive data—log only hashes or truncated values.

### 5. **Cost Tracking & Reporting**
- **Per-User/Per-Key Cost Tracking:**
  - Store usage and cost data in DynamoDB, keyed by API key or user.
  - Publish cost metrics to CloudWatch for alerting and reporting.
- **Automated Reporting:**
  - Plan for future dashboards or automated cost reports (email, Slack, etc.).

### 6. **Documentation & Onboarding**
- **Update and Expand Documentation:**
  - Document all environment variables, secrets, and configuration options.
  - Provide a clear onboarding guide for new users and contributors.
  - Add architecture diagrams and API usage examples.
- **CLI and API Reference:**
  - Ensure CLI and API endpoints are fully documented, with example requests and responses.

### 7. **Future Deliverables and Enhancements**
- **Admin UI (Optional):**
  - Plan for a web-based admin UI for API key and usage management.
- **Advanced Analytics:**
  - Integrate with billing and analytics platforms for deeper insights.
- **Bulk Operations:**
  - Add support for bulk key creation/import/export in the CLI.
- **Notification Integrations:**
  - Integrate with email, Slack, or other systems for alerts and notifications.
- **Granular Permission Management:**
  - Add support for more granular, per-key or per-user permissions if needed.

---

## Key Principles
- **Security**: OIDC for CI/CD, hashed API keys, least-privilege IAM, no plaintext secrets.
- **Configurability**: All deployment/runtime config via variables/secrets.
- **Cost Awareness**: Track/report per-user Bedrock costs as a core feature.
- **Maintainability**: Modular code, clear docs, automated tests, and CI/CD.

---

**Next milestone:**
> Successfully return a real LLM response from the deployed API, via LiteLLM proxying to Bedrock, using the OpenAI-compatible or MCP API.

This document reflects the current state and priorities for Pennyworth, and is suitable for handoff or further discussion in a new context. 