# Pennyworth CLI Authentication & Permissions: Cognito + IAM

This document describes, in detail, how authentication and permissions for the Pennyworth CLI tool are managed using Amazon Cognito and AWS IAM, what is automated via AWS SAM, what must be done manually, and how this can be deployed from a GitHub Action.

---

## 1. Overview
- **Goal:** Only authorized users can use the CLI tool to manage API keys, with all actions performed using temporary, auditable AWS credentials.
- **Solution:**
  - Use **Cognito User Pool** for user authentication (username/password, optional MFA).
  - Use **Cognito Identity Pool** to issue temporary AWS credentials to authenticated users.
  - Use an **IAM Role** (e.g., `PennyworthAdminRole`) with permissions for DynamoDB, assumed by authenticated Cognito users.
  - Use **AWS SAM** to automate all infrastructure except user onboarding.

---

## 2. Automated Setup with AWS SAM

### What SAM Can Automate
- **Cognito User Pool** (with password policy, MFA, etc.)
- **Cognito User Pool Client** (for CLI authentication)
- **Cognito Identity Pool** (linked to User Pool)
- **IAM Role** for CLI admins, with trust policy for Cognito
- **Role mapping** in Identity Pool (authenticated users → admin role)
- **DynamoDB Table** for API keys
- **Outputs** for all ARNs, IDs, and endpoints needed by the CLI

### What Must Be Done Manually
- **User creation/invitation:** Add users to the Cognito User Pool via AWS Console, CLI, or API.
- **Group membership:** (Optional) If using Cognito groups for finer-grained permissions, manage via Console/API.
- **MFA setup:** Users set up MFA at first login (if required).

---

## 3. Permissions Flow

1. **User is created/invited** in the Cognito User Pool (manual, one-time).
2. **User authenticates** via the CLI (username/password, optional MFA).
3. **CLI exchanges credentials** for a Cognito ID token.
4. **CLI uses the ID token** to get temporary AWS credentials from the Cognito Identity Pool.
5. **CLI uses these credentials** to perform DynamoDB actions as the `PennyworthAdminRole`.
6. **IAM enforces permissions**; all actions are logged and auditable.

---

## 4. Example SAM Template (High-Level)

```yaml
Resources:
  PennyworthUserPool:
    Type: AWS::Cognito::UserPool
    Properties: { ... }

  PennyworthUserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties: { ... }

  PennyworthIdentityPool:
    Type: AWS::Cognito::IdentityPool
    Properties:
      CognitoIdentityProviders:
        - ClientId: !Ref PennyworthUserPoolClient
          ProviderName: !GetAtt PennyworthUserPool.ProviderName
      ...

  PennyworthAdminRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument: # Trust policy for Cognito
      Policies: [ ... DynamoDB permissions ... ]

  IdentityPoolRoleAttachment:
    Type: AWS::Cognito::IdentityPoolRoleAttachment
    Properties:
      IdentityPoolId: !Ref PennyworthIdentityPool
      Roles:
        authenticated: !GetAtt PennyworthAdminRole.Arn

  ApiKeysTable:
    Type: AWS::DynamoDB::Table
    Properties: { ... }
```

### Outputs
- User Pool ID
- User Pool Client ID
- Identity Pool ID
- Admin Role ARN
- DynamoDB Table Name

---

## 5. CLI Authentication Flow (User Experience)

1. **User is invited to Cognito User Pool** (admin task, one-time).
2. **User runs the CLI tool.**
3. **CLI prompts for username/password** (and MFA if enabled).
4. **CLI exchanges credentials for a Cognito ID token.**
5. **CLI uses the ID token to get temporary AWS credentials** from the Identity Pool.
6. **CLI uses these credentials to perform all actions.**
7. **All permissions are enforced by IAM.**

---

## 6. Deploying from a GitHub Action

### What Works Well
- **All infrastructure (User Pool, Identity Pool, IAM Role, DynamoDB Table) can be deployed/updated from a GitHub Action** using AWS SAM and the AWS CLI.
- **Outputs** (IDs, ARNs) can be captured and published as GitHub Action outputs or artifacts for later use.

### Caveats & Best Practices
- **User onboarding (creation/invitation) is still a manual step.**
- **GitHub Action must have permissions to create/update Cognito, IAM, and DynamoDB resources.**
- **Sensitive outputs (e.g., User Pool Client Secret) should be handled as GitHub secrets.**
- **If you use GitHub OIDC for deployment, ensure the deploy role has all necessary permissions.**
- **CLI configuration (User Pool ID, Client ID, Identity Pool ID, Region) should be published as outputs or stored in a secure location for CLI users.**

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
- **All CLI actions are performed with temporary AWS credentials, mapped to the admin IAM role.**
- **All actions are logged in AWS CloudTrail and DynamoDB streams (if enabled).**
- **No static AWS keys are used.**
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
| DynamoDB Table              | Yes               |                 |
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
- [AWS::DynamoDB::Table](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)

---

For further questions or to update this process, see the project documentation or contact the maintainers. 