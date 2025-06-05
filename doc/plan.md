# Project Plan: pennyworth

## Project Context

- The core goal: Deploy a working LiteLLM proxy to Bedrock (or another LLM), exposing an OpenAI-compatible and/or MCP API endpoint, accessible via API Gateway and Lambda.
- Supporting infrastructure (API Gateway, Lambda, custom domain, DynamoDB, Cognito, CI/CD, log retention) is in place and operational.
- The project is licensed AGPL-3.0-only, and follows a zero-cost-at-rest, serverless-first philosophy.

---

## Current Status
- Automated, secure AWS SAM deployment pipeline is live
- Lambda function and API Gateway endpoint deployed
- Custom domain (e.g., https://api.uproro.com/v1/hello) is working
- GitHub Actions CI/CD with OIDC and least-privilege IAM is operational
- DynamoDB and Cognito resources are provisioned
- Log retention automation for Lambda log groups is in place
- Documentation and workflow are up to date

---

## **Immediate Next Steps: Minimum Viable LLM Proxy**

### 1. **Integrate LiteLLM with Bedrock (or other LLM) in Lambda**
- Package LiteLLM and all dependencies with the Lambda function.
- Configure LiteLLM to use Bedrock (or another LLM provider):
  - Set up credentials, region, and model selection.
  - Ensure Lambda handler routes OpenAI/MCP requests to LiteLLM.
- Add/configure environment variables as needed for LLM provider.

### 2. **Update Lambda Permissions**
- Ensure the Lambda execution role has `bedrock:InvokeModel` (and any other required) permissions.

### 3. **Expose OpenAI-Compatible and/or MCP Endpoints**
- Update the SAM template/API Gateway configuration to expose the correct paths (e.g., `/v1/chat/completions`, `/mcp/...`).
- Ensure HTTP methods and CORS settings match client expectations.

### 4. **End-to-End Test: Client → API Gateway → Lambda (LiteLLM) → Bedrock → Response**
- Use curl, Postman, or an OpenAI-compatible client to send a request to the deployed endpoint.
- Confirm a real LLM response is returned.
- Debug and iterate on Lambda/API Gateway as needed until this works.

---

## **Supporting Tasks (After LLM Proxy is Live)**

### 5. **CLI Tool for API Key Management**
- Scaffold Python CLI for API key management (create, audit, revoke, rotate)
- Integrate CLI with Cognito authentication and DynamoDB
- Document CLI usage and onboarding

### 6. **Security & IAM Hardening**
- Restrict IAM policies to least privilege for all roles
- Replace wildcards in `iam:PassRole` and other permissions with specific ARNs
- Regularly review and audit IAM roles and policies
- Enable and test MFA for all admin access

### 7. **Monitoring, Logging, and Observability**
- Add CloudWatch metrics and alarms for Lambda and API Gateway
- Set up dashboards for operational visibility
- Implement alerting for errors, cost spikes, and suspicious activity

### 8. **Cost Tracking & Reporting**
- Track per-user and per-key usage and cost in DynamoDB
- Publish usage and cost metrics to CloudWatch
- Plan for future dashboards and automated reporting/alerts

### 9. **Documentation & Onboarding**
- Update and maintain deployment, architecture, and security documentation
- Provide onboarding guide for new users and contributors
- Document all environment variables, secrets, and configuration options

### 10. **Future Deliverables**
- Admin UI (web-based) for API key and usage management (optional, CLI is current plan)
- Advanced analytics and billing integration
- Bulk key creation/import/export in CLI
- Integration with notification systems (email, Slack)
- More granular permission management

---

## Key Principles
- **Security:** OIDC for CI/CD, hashed API keys, least-privilege IAM, no plaintext secrets
- **Configurability:** All deployment and runtime config via variables/secrets, not hard-coded
- **Cost Awareness:** Track and report per-user Bedrock costs as a core feature
- **Maintainability:** Modular code, clear docs, automated tests, and CI/CD

---

**Next milestone:**
> A real LLM response returned from the deployed API, via LiteLLM proxying to Bedrock (or another LLM), using the OpenAI-compatible or MCP API.

This plan provides a clear, up-to-date roadmap for pennyworth, focusing on security, scalability, cost-awareness, and developer experience. 