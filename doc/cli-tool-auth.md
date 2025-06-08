# Pennyworth CLI Authentication & Permissions: Cognito + REST API

This document describes, in detail, how authentication and permissions for the Pennyworth CLI tool are managed using Amazon Cognito and REST API endpoints, what is automated via AWS SAM, what must be done manually, and how this can be deployed from a GitHub Action.

---

## 1. Overview
- **Goal:** Only authorized users can use the CLI tool to manage API keys, with all actions performed via authenticated REST API calls.
- **Solution:**
  - Use **Cognito User Pool** for user authentication (username/password, optional MFA).
  - CLI exchanges credentials for a Cognito ID token (JWT).
  - CLI uses the JWT as a Bearer token for all REST API requests.
  - All API key management (create, rotate, revoke, audit, status) is performed via REST API endpoints.
  - No direct AWS SDK or DynamoDB access from the CLI.

---

## 2. Automated Setup with AWS SAM

### What SAM Can Automate
- **Cognito User Pool** (with password policy, MFA, etc.)
- **Cognito User Pool Client** (for CLI authentication)
- **Cognito Identity Pool** (linked to User Pool)
- **IAM Role** for CLI admins, with trust policy for Cognito
- **Role mapping** in Identity Pool (authenticated users → admin role)
- **Outputs** for all ARNs, IDs, and endpoints needed by the CLI

### What Must Be Done Manually
- **User creation/invitation:** Add users to the Cognito User Pool via AWS Console, CLI, or API.
- **Group membership:** (Optional) If using Cognito groups for finer-grained permissions, manage via Console/API.
- **MFA setup:** Users set up MFA at first login (if required).

---

## 3. Permissions Flow

1. **User is created/invited** in the Cognito User Pool (manual, one-time).
2. **User authenticates** via the CLI (username/password, optional MFA).
3. **CLI exchanges credentials for a Cognito ID token (JWT).**
4. **CLI uses the JWT as a Bearer token for all REST API requests.**
5. **REST API enforces permissions and performs all key management actions.**
6. **All actions are logged and auditable.**

---

## 4. Example REST API Flow (High-Level)

- CLI authenticates with Cognito and obtains a JWT.
- CLI sends HTTP requests to REST API endpoints (e.g., `/users`, `/users/{id}/apikey`).
- REST API validates the JWT and enforces permissions based on Cognito groups/roles.
- All key management is performed by the backend, not the CLI.

### Outputs
- User Pool ID
- User Pool Client ID
- REST API base URL

---

## 5. CLI Authentication Flow (User Experience)

1. **User is invited to Cognito User Pool** (admin task, one-time).
2. **User runs the CLI tool.**
3. **CLI prompts for username/password** (and MFA if enabled).
4. **CLI exchanges credentials for a Cognito ID token (JWT).**
5. **CLI uses the JWT as a Bearer token for all REST API requests.**
6. **All permissions are enforced by the REST API.**

---

## 6. Deploying from a GitHub Action

### What Works Well
- **All infrastructure (User Pool, Identity Pool, IAM Role) can be deployed/updated from a GitHub Action** using AWS SAM and the AWS CLI.
- **Outputs** (IDs, ARNs) can be captured and published as GitHub Action outputs or artifacts for later use.

### Caveats & Best Practices
- **User onboarding (creation/invitation) is still a manual step.**
- **GitHub Action must have permissions to create/update Cognito and IAM resources.**
- **Sensitive outputs (e.g., User Pool Client Secret) should be handled as GitHub secrets.**
- **If you use GitHub OIDC for deployment, ensure the deploy role has all necessary permissions.**
- **CLI configuration (User Pool ID, Client ID, REST API URL, Region) should be published as outputs or stored in a secure location for CLI users.**

### Example GitHub Action Step
```yaml
- name: Deploy Pennyworth Infra
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
    aws-region: us-west-2
- name: Deploy with SAM
  run: |
    sam deploy --stack-name pennyworth-infra --capabilities CAPABILITY_IAM
- name: Export Outputs
  run: |
    aws cloudformation describe-stacks --stack-name pennyworth-infra --query "Stacks[0].Outputs"
```

---

## 7. Security & Audit
- **All CLI actions are performed via authenticated REST API calls.**
- **All actions are logged in API Gateway, Lambda, and CloudTrail (if enabled).**
- **No static AWS keys or direct AWS SDK access is used by the CLI.**
- **User management is separate from infrastructure and can be handled securely via the AWS Console.**

---

## 8. Summary Table
| Step                        | Automated by SAM? | Manual?         |
|-----------------------------|-------------------|-----------------|
| Cognito User Pool           | Yes               |                 |
| Cognito User Pool Client    | Yes               |                 |
| Cognito Identity Pool       | Yes               |                 |
| IAM Role (Admin)            | Yes               |                 |
| Role Mapping                | Yes               |                 |
| REST API Endpoints          | Yes               |                 |
| User creation/invitation    |                   | Yes             |
| Group membership            |                   | (Optional)      |
| MFA setup                   |                   | User at login   |

---

## 9. References
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/)
- [Cognito User Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html)
- [Cognito Identity Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-identity.html)
- [AWS::Cognito::UserPool](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html)
- [AWS::Cognito::IdentityPool](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypool.html)
- [AWS::IAM::Role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html)

---

For further questions or to update this process, see the project documentation or contact the maintainers. 