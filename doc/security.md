# Security Overview (Current State)

## Introduction
Pennyworth uses Amazon Cognito and REST API endpoints for all authentication and authorization. There is no DynamoDB, no plaintext API key storage, and no direct AWS SDK/database access for clients. Security controls are implemented through least-privilege IAM, HTTPS, and structured logging.

---

## 1. Authentication Model

### API Key Authentication
- API keys are stored as Cognito custom attributes (never plaintext after creation).
- All API key validation is performed via REST endpoints and Cognito lookups.
- API keys are only shown once at creation; never stored or returned in plaintext.

### Cognito JWT Authentication
- All user authentication is via Cognito User Pool JWTs.
- JWTs are validated in `auth.py` for every request to protected endpoints.
- JWTs are exchanged for AWS credentials via Cognito Identity Pool for user-context AWS operations.

---

## 2. Authorization Model

### Centralized Authorization
- All authorization logic is in `auth.py` and handler middleware.
- Permissions and roles are managed via Cognito groups and custom attributes.

### Least-Privilege IAM
- Lambda and user roles are tightly scoped.
- Lambda assumes user-context roles only as needed for specific operations.

---

## 3. API Key Management
- All key management (creation, rotation, revocation) is via REST endpoints.
- Only authorized users (admins) can create, rotate, or revoke keys.
- CLI and clients interact only via REST API; never direct AWS SDK or database access.

---

## 4. User Management
- Users are created via REST endpoints and assigned to groups for permissions.
- Passwords are set via secure REST endpoints; never logged or stored in plaintext.
- Access to endpoints and operations is controlled by Cognito group membership.

---

## 5. Secrets Management
- No secrets (API keys, credentials) are ever hardcoded in code or configuration files.
- All configuration is via environment variables and Cognito; never hardcoded.
- See the [README](../README.md) for details on environment variable naming and configuration conventions.
- All project-specific environment variables are prefixed with `PENNYWORTH_` (e.g., `PENNYWORTH_BASE_DOMAIN`, `PENNYWORTH_API_URL`, etc.).
- All configuration constants are centralized in `src/shared/constants/__init__.py`.

---

## 6. Transport Security
- All endpoints are served via HTTPS (API Gateway + ACM).
- No HTTP fallback is permitted.

---

## 7. Audit Logging and Observability
- All authentication, authorization, and key management actions are logged with context using Powertools Logger.
- All logs and traces are sent to CloudWatch and X-Ray for monitoring and audit.
- Log retention is set via CI/CD (e.g., 14 days).

---

## 8. CI/CD Security
- Deployments use OIDC and a tightly scoped IAM role for GitHub Actions.
- No hardcoded credentials in CI/CD workflows.
- Git commit SHA is tracked in the deployed environment and exposed via the `/v1/version` endpoint.

---

## 9. Best Practices and Recommendations
- Rotate API keys and credentials regularly.
- Use strong passwords and MFA for Cognito users.
- Restrict admin access to key management endpoints.
- Monitor logs and traces for suspicious activity.
- Review IAM policies and group memberships regularly.

---

## 10. Security Controls Summary Table

| Area                | Control/Practice                                  |
|---------------------|---------------------------------------------------|
| Authentication      | Cognito JWTs, API keys (Cognito custom attributes)|
| Authorization       | Centralized in `auth.py`, Cognito groups          |
| Key Management      | REST endpoints only, no plaintext storage         |
| User Management     | REST endpoints, group-based permissions           |
| Secrets Management  | No secrets in code, env vars only                 |
| Transport Security  | HTTPS everywhere (API Gateway + ACM)              |
| Logging             | Structured logs via Powertools, CloudWatch        |
| Tracing             | X-Ray enabled for all handlers                    |
| CI/CD               | OIDC, least-privilege IAM, no hardcoded creds     |
| Audit               | All actions logged, log retention via CI/CD       |

---

This security model implements centralized authentication and authorization, API key and user management via Cognito and REST, least-privilege IAM, and audit logging. Clients do not have direct access to AWS resources or secrets. 