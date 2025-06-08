# Project Plan & Current State: Pennyworth

## Project Overview
Pennyworth is a serverless, OpenAI-compatible API proxy for AWS Bedrock (and other LLMs), designed for secure, zero-cost-at-rest operation. It leverages AWS Lambda, API Gateway, Cognito (as the single source of truth for users and API keys), and supporting AWS infrastructure, with a focus on least-privilege IAM, CI/CD automation, and maintainability. The project is licensed AGPL-3.0-only.

---

## Current State (as of latest refactor)

### Codebase & Architecture
- **Single Lambda Entrypoint:** All routing is handled in `src/lambda/api.py` using AWS Lambda Powertools' event handler decorators.
- **Modular Handlers:** All business logic is delegated to handler modules in `src/lambda/handlers/` (`openai.py`, `mcp.py`, `well_known.py`, `protected.py`).
- **Centralized Authentication:** All API key and Cognito JWT authentication is handled in `src/lambda/auth.py` with a strict, auditable, default-deny approach.
- **Logging:** Uses AWS Lambda Powertools logger, instantiated in `src/lambda/utils.py` and imported where needed.
- **Consistent Endpoint Versioning:** All endpoints are under `/v1` for future-proofing and clarity.
- **Environment Variables:** All configuration is via environment variables, with no secrets in code.

### Infrastructure
- **API Gateway:** Routes all `/v1/*` traffic to the Lambda function.
- **Lambda:** Handles all OpenAI-compatible and MCP API requests, authenticates via API keys or Cognito JWTs, and proxies to Bedrock via LiteLLM.
- **Cognito:** Used as the single source of truth for all users and API keys. All user and key management, permissions, and status checks are centralized in Cognito.
- **IAM:** All roles are least-privilege and tightly scoped, with role mappings based on Cognito groups.
- **CloudWatch:** All logs are collected and retained for 14 days.

### Security
- **Centralized, auditable authentication** for all endpoints.
- **No plaintext API keys** are stored or logged.
- **No static AWS credentials**; all access is via IAM roles and OIDC.
- **API keys are cryptographically secure, unique, and stored as custom attributes on Cognito users.**

### What is Working
- End-to-end deployment and infrastructure provisioning via CI/CD.
- Modular, maintainable Lambda codebase with clear separation of concerns.
- API Gateway and Lambda are live and reachable at the custom domain.
- Logging and error handling are robust and centralized.
- Documentation is up to date and in-repo.

---

## Next Steps / Detailed Plan

### 0. Cognito & IAM Setup (template.yaml)
- **Single Cognito User Pool** for all users (admins, regular users, etc.).
- **Cognito Groups** (e.g., `admin`, `user`) for role-based access.
- **Cognito Identity Pool** federated with the user pool.
- **IAM Roles and Policies:**
  - `AdminRole`: Can perform all user management actions (CRUD users, manage API keys, assign groups, call Cognito admin APIs).
  - `UserRole`: Can only read/update their own user attributes (e.g., rotate/revoke their own API key).
- **Role Mappings:**
  - Users in the `admin` group get the `AdminRole`.
  - All other users get the `UserRole`.
- **CloudFormation/SAM Resources:**
  - Cognito User Pool, User Pool Groups, Identity Pool, IAM Roles, Role Attachments, and Role Mappings (see detailed YAML in previous message).

### 1. Endpoints for CRUD Operations on Cognito Users and API Keys
- **/users (POST):** Create user (admin only, can specify group/role; default is user).
- **/users/{id} (GET):** Get user info (admin for any user, user for self).
- **/users/{id} (PUT/PATCH):** Update user (admin for any user, user for self).
- **/users/{id} (DELETE):** Delete user (admin only).
- **/users/{id}/apikey (POST):** Rotate API key (admin for any user, user for self).
- **/users/{id}/apikey (DELETE):** Revoke API key (admin for any user, user for self).

**Auth:**
- Endpoints for user management require Cognito JWT (ID token).
- Use group membership to authorize admin actions.
- Endpoints for API key-based access (e.g., LLM proxy) use API key only.

### 2. User Creation, Group Assignment, and API Key Management
- When creating a user, allow specifying group (default: user).
- Use Cognito admin APIs to assign group.
- Generate a cryptographically secure API key (`secrets.token_urlsafe(32)`) and store as a custom attribute (e.g., `custom:api_key`) on the user.
- To rotate: generate a new key, update the custom attribute.
- To revoke: remove the custom attribute or disable the user.

### 3. API Key Authentication and Permission Checks
- On API key-authenticated requests:
  - Lookup user by API key (custom attribute) using Cognito `ListUsers`.
  - Use Cognito user status and group for all permission checks.
  - If the user is not found, disabled, or lacks permission, the operation fails.
- On Cognito JWT-authenticated requests:
  - Use group membership in the JWT to authorize actions.

### 4. Retrofitting Existing API Key Code
- Remove DynamoDB for API key lookup.
- Use Cognito `ListUsers` with filter on `custom:api_key`.
- Use Cognito user status and group for all permission checks.

### 5. Endpoint Auth Model

| Endpoint                        | Auth Method      | Who Can Access         | Notes                        |
|----------------------------------|------------------|------------------------|------------------------------|
| /users (POST)                    | Cognito JWT      | Admins                 | Create user, assign group    |
| /users/{id} (GET/PUT/DELETE)     | Cognito JWT      | Admins (any), Users (self) | CRUD user info           |
| /users/{id}/apikey (POST/DELETE) | Cognito JWT      | Admins (any), Users (self) | Rotate/revoke API key   |
| /llm-proxy, /models, etc.        | API Key          | Any valid user         | Lookup by API key            |
| /parameters/well-known           | Public           | Anyone                 | No auth required             |

### 6. Additional Details & Best Practices
- **Key Generation:** Use `secrets.token_urlsafe(32)` for 256-bit keys.
- **Key Storage:** Store as `custom:api_key` on Cognito user.
- **Key Lookup:** Use `ListUsers(Filter='custom:api_key="..."')`.
- **Key Revocation:** Remove attribute or disable user.
- **Group Assignment:** Use `admin_add_user_to_group`.
- **Permissions:** Enforced by IAM roles mapped via Identity Pool.
- **Auditing:** Log all actions with user ID and endpoint.
- **Testing:** Write integration tests for all flows, including edge cases.
- **Security:** Never expose the API key after creation; mask in logs.
- **Documentation:** Document the API, key management, and permission model for future maintainers.

### 7. **Monitoring, Logging, and Observability**
- Add custom CloudWatch metrics and alarms for Lambda invocations, errors, and latency.
- Create CloudWatch dashboards for operational visibility.
- Ensure logs never contain full API keys or sensitive data.

### 8. **Cost Tracking & Reporting**
- Store usage and cost data in a suitable store, keyed by API key or user. (No longer using DynamoDB for authentication or API key management.)
- Publish cost metrics to CloudWatch for alerting and reporting.
- Plan for future dashboards or automated cost reports.

### 9. **Documentation & Onboarding**
- Update and expand documentation for environment variables, secrets, and configuration.
- Provide onboarding guide and architecture diagrams.
- Ensure CLI and API endpoints are fully documented with examples.

### 10. **Future Enhancements**
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
- **Single Source of Truth:** Cognito is the only source of truth for users and API keys.

---

**Next milestone:**
> Successfully return a real LLM response from the deployed API, via LiteLLM proxying to Bedrock, using the OpenAI-compatible or MCP API, with all authentication and authorization managed via Cognito and IAM as described above.

This document reflects the current state and priorities for Pennyworth, and is suitable for handoff or further discussion in a new context. 