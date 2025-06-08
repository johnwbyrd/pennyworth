# Security Guide

## API Key Management (Cognito)

### Overview
API keys are used to authenticate and authorize access to the OpenAI-compatible API proxy. **API keys are stored as custom attributes (e.g., `custom:api_key`) on Cognito users—never the key itself after creation.** This ensures that even if the user directory is compromised, the actual keys remain secret. **API key management is exclusively via REST API endpoints; the CLI is a REST client.**

### Cognito Attribute Design
- **Attribute Name:** `custom:api_key` (or similar)
- **Stored On:** Cognito user object
- **Attributes:**
  - `custom:api_key` (securely generated, only shown once)
  - `status` (active, revoked, expired)
  - `permissions` (optional, as Cognito attribute)
  - `expiry` (optional)

### Key Generation and Authentication
- When creating a key:
  - Generate a strong random API key (256 bits, base64 or hex encoded)
  - Store as a Cognito custom attribute on the user
  - Distribute the API key to the user securely (show once)
- When authenticating:
  - Lookup user by API key (using Cognito `ListUsers` with filter on `custom:api_key`)
  - If found and active, allow access; otherwise, deny

### Key Lifecycle
- **Creation:**
  - Generate a secure random key
  - Store as Cognito custom attribute with status `active`
  - Distribute the key to the user securely
- **Rotation:**
  - Create a new key, update user/client, then revoke the old key
  - Support overlapping keys during transition
- **Revocation:**
  - Remove the attribute or set status to `revoked` in Cognito
  - Key is immediately invalid for new requests
- **Expiration:**
  - Optionally set expiry date as a Cognito attribute

### Best Practices
- Use strong, random keys (never guessable)
- **Never store or log full API keys**—only store as Cognito attribute, and only show to user once
- Rotate keys regularly (e.g., every 90 days)
- Revoke keys immediately if compromised
- Monitor usage for anomalies (spikes, abuse)
- Use HTTPS for all API traffic

## IAM and Lambda Permissions

- **Lambda Execution Role:**
  - Grant only the permissions needed:
    - `cognito-idp:ListUsers` (for key validation)
    - `cognito-idp:AdminUpdateUserAttributes` (for key rotation/revocation)
    - `bedrock:InvokeModel` or other LLM provider permissions
    - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` (for CloudWatch)
- **API Gateway:**
  - Restrict invocation to your Lambda only
  - Enable throttling and quotas

## General Security Recommendations
- Use environment variables for all secrets and credentials
- Never hard-code secrets in code or config files
- Enable CloudWatch logging and monitor for suspicious activity
- Use AWS IAM best practices (least privilege, role separation)
- Regularly review and audit permissions and access logs
- Consider enabling AWS WAF for API Gateway for additional protection
- **MCP protocol support is a near-term requirement for compatibility with VS Code, Cursor, and similar tools.**

## Debugging and Monitoring
- **CloudWatch Logs:** All Lambda logs (including errors, print/console.log statements, and stack traces) are available in AWS Console → CloudWatch → Logs.
- **CloudWatch Metrics:** Monitor Lambda invocations, errors, and performance in CloudWatch → Metrics.
- **Sensitive Data:** Never log full API keys or other secrets. Log only hashes or truncated values for debugging.
- **Best Practices:** Log key events (authentication attempts, permission checks, errors) with enough context for troubleshooting, but always redact or omit sensitive data.

---

This security model provides strong, flexible, and auditable API key management, while leveraging AWS's security best practices for serverless deployments. API keys are never stored in plaintext after creation, ensuring robust protection even if the user directory is compromised. 