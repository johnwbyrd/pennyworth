# Project Plan: pennyworth

## Project Goals
- Provide an OpenAI-compatible API proxy for AWS Bedrock models (Claude, Titan, etc.)
- Support secure, zero-cost-at-rest, serverless deployment on AWS (Lambda, API Gateway, DynamoDB)
- Enable per-user (API key/account) usage and cost tracking, with future reporting and alerting
- Integrate with modern developer tools (VS Code, Cursor, etc.)
- Use best practices for security, observability, and maintainability
- Minimize hard-coding; use variables and secrets for all configuration

## Major Phases & Deliverables

### 1. Architecture & Design
- Define high-level architecture (API Gateway → Lambda (LiteLLM) → Bedrock)
- Document security model (API key hashing, OIDC, IAM roles)
- Specify configuration via environment variables, GitHub secrets, and repository variables

### 2. Deployment Automation
- Set up GitHub Actions workflow for CI/CD using OIDC (no static AWS keys)
- Parameterize all deployment values (region, domain, stack name, role ARN, etc.)
- Use AWS SAM/CloudFormation for infrastructure as code
- Automate Route 53, ACM, and API Gateway custom domain setup

### 3. API Key Management
- Design DynamoDB schema for API keys (hashed keys, permissions, account_id, usage counters)
- Implement secure key creation, rotation, and revocation
- Enforce authentication and permission checks in Lambda handler

### 4. Usage & Cost Tracking
- Track per-call usage (tokens, model, endpoint) and associate with API key/account
- Calculate Bedrock cost per call using token counts and pricing table
- Publish per-user cost and usage as custom CloudWatch metrics (future: dashboards, alerts)
- Store usage/cost data in DynamoDB for reporting and analytics

### 5. Client Integration
- Ensure OpenAI-compatible endpoints work with VS Code, Cursor, and other clients
- Provide example client configs and onboarding docs
- Test streaming, large requests, and error handling

### 6. Monitoring & Observability
- Log all requests, errors, and key events to CloudWatch (with sensitive data redacted)
- Publish custom metrics for usage, cost, and errors
- Set up dashboards and alarms for operational visibility

### 7. Documentation & Onboarding
- Write and maintain clear README.md, architecture, deployment, and security docs
- Document all environment variables, secrets, and configuration options
- Provide onboarding guide for new users and contributors

## Key Principles
- **Security:** OIDC for CI/CD, hashed API keys, least-privilege IAM, no plaintext secrets
- **Configurability:** All deployment and runtime config via variables/secrets, not hard-coded
- **Cost Awareness:** Track and report per-user Bedrock costs as a core feature
- **Maintainability:** Modular code, clear docs, automated tests, and CI/CD

## Future Deliverables
- Per-user cost dashboards and automated reporting/alerts
- Admin UI or CLI for API key and usage management
- Advanced analytics and billing integration

---

This plan provides a clear roadmap for pennyworth, ensuring a secure, scalable, and cost-aware OpenAI-compatible API proxy for AWS Bedrock. 