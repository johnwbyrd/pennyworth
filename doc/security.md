# Security Guide

## API Key Management (DynamoDB)

### Overview
API keys are used to authenticate and authorize access to the OpenAI-compatible API proxy. **Only a secure hash (e.g., SHA-256) of each API key is stored in DynamoDB—never the key itself.** This ensures that even if the database is compromised, the actual keys remain secret.

### DynamoDB Table Design
- **Table Name:** `api-keys` (or configurable)
- **Primary Key:** `api_key_hash` (string, securely generated hash)
- **Attributes:**
  - `created_at` (timestamp)
  - `status` (active, revoked, expired)
  - `owner` (user/team/tenant identifier)
  - `permissions` (encrypted or plaintext map/list)
  - `last_used` (timestamp, optional)
  - `usage_count` (optional)
  - `rate_limit` (optional)

### Key Hashing and Authentication
- When creating a key:
  - Generate a strong random API key (256 bits, base64 or hex encoded)
  - Compute a secure hash (e.g., SHA-256) of the API key
  - Store only the hash in DynamoDB, never the plaintext key
  - Distribute the API key to the user securely (show once)
- When authenticating:
  - Hash the presented API key using the same hash function
  - Look up the hash in DynamoDB
  - If found and active, allow access; otherwise, deny

### Key Lifecycle
- **Creation:**
  - Generate a secure random key
  - Store its hash in DynamoDB with status `active`
  - Distribute the key to the user securely
- **Rotation:**
  - Create a new key, update user/client, then revoke the old key
  - Support overlapping keys during transition
- **Revocation:**
  - Set `status` to `revoked` in DynamoDB
  - Key is immediately invalid for new requests
- **Expiration:**
  - Optionally set TTL or expiration date for keys

### Best Practices
- Use strong, random keys (never guessable)
- **Never store or log full API keys**—only store their hashes
- Rotate keys regularly (e.g., every 90 days)
- Revoke keys immediately if compromised
- Monitor usage for anomalies (spikes, abuse)
- Use HTTPS for all API traffic

## IAM and Lambda Permissions

- **Lambda Execution Role:**
  - Grant only the permissions needed:
    - `dynamodb:GetItem` (for key validation)
    - `dynamodb:UpdateItem` (for usage tracking, optional)
    - `bedrock:InvokeModel` or other LLM provider permissions
    - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` (for CloudWatch)
- **API Gateway:**
  - Restrict invocation to your Lambda only
  - Enable throttling and quotas
- **DynamoDB Table:**
  - Restrict access to Lambda's execution role
  - Enable point-in-time recovery (optional)

## General Security Recommendations
- Use environment variables for all secrets and credentials
- Never hard-code secrets in code or config files
- Enable CloudWatch logging and monitor for suspicious activity
- Use AWS IAM best practices (least privilege, role separation)
- Regularly review and audit permissions and access logs
- Consider enabling AWS WAF for API Gateway for additional protection

## Debugging and Monitoring
- **CloudWatch Logs:** All Lambda logs (including errors, print/console.log statements, and stack traces) are available in AWS Console → CloudWatch → Logs.
- **CloudWatch Metrics:** Monitor Lambda invocations, errors, and performance in CloudWatch → Metrics.
- **Sensitive Data:** Never log full API keys or other secrets. Log only hashes or truncated values for debugging.
- **Best Practices:** Log key events (authentication attempts, permission checks, errors) with enough context for troubleshooting, but always redact or omit sensitive data.

---

This security model provides strong, flexible, and auditable API key management, while leveraging AWS's security best practices for serverless deployments. API keys are never stored in plaintext, ensuring robust protection even if the database is compromised. 