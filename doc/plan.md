# Project Plan: pennyworth

## Current Status
- Automated, secure AWS SAM deployment pipeline is live
- Lambda function and API Gateway endpoint deployed
- Custom domain (e.g., https://api.uproro.com/hello) is working via Route 53 and ACM
- GitHub Actions CI/CD with OIDC and least-privilege IAM is operational
- Documentation and workflow are up to date

---

## Next Steps & Major Tasks

### 1. Expand SAM Template Toward Production Architecture
- Add Cognito User Pool and Identity Pool for authentication
- Add DynamoDB table for API key management
- Add additional Lambda functions for OpenAI-compatible endpoints and MCP support
- Parameterize and document all environment variables and secrets
- Add explicit `AWS::Serverless::Api` resource for more control (if needed)

### 2. Build and Integrate the CLI Tool
- Scaffold Python CLI for API key management (create, audit, revoke, rotate)
- Integrate CLI with Cognito authentication and DynamoDB
- Support output in both JSON and human-friendly text
- Document CLI usage and onboarding

### 3. API Gateway & Client Compatibility
- Update API Gateway configuration for versioned paths (e.g., `/v1/hello`)
- Set up and test custom domain with versioned endpoints
- Ensure compatibility with VS Code, Cursor, and other clients
- Implement and test MCP protocol support

### 4. Security & IAM Hardening
- Restrict IAM policies to least privilege for all roles
- Replace wildcards in `iam:PassRole` and other permissions with specific ARNs
- Regularly review and audit IAM roles and policies
- Enable and test MFA for all admin access

### 5. Monitoring, Logging, and Observability
- Add CloudWatch log groups, metrics, and alarms for Lambda and API Gateway
- Set up dashboards for operational visibility
- Implement alerting for errors, cost spikes, and suspicious activity

### 6. Documentation & Onboarding
- Update and maintain deployment, architecture, and security documentation
- Provide onboarding guide for new users and contributors
- Document all environment variables, secrets, and configuration options

### 7. Cost Tracking & Reporting
- Track per-user and per-key usage and cost in DynamoDB
- Publish usage and cost metrics to CloudWatch
- Plan for future dashboards and automated reporting/alerts

### 8. Future Deliverables
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

This plan provides a clear roadmap for pennyworth, ensuring a secure, scalable, and cost-aware OpenAI-compatible API proxy for AWS Bedrock and modern developer tools. 