# Deployment Guide

## Overview
This guide describes how to deploy **pennyworth** (the LiteLLM-based OpenAI-compatible API proxy) on AWS Lambda, with API Gateway as the HTTP entry point. It covers environment setup, deployment options, and special considerations for long-running and large requests. **For production, we recommend using GitHub Actions with OIDC for secure, temporary AWS credentials.**

## Prerequisites
- AWS account with Lambda, API Gateway, Route 53, ACM, and IAM permissions in **us-west-2**
- AWS CLI configured (for initial setup)
- Node.js 18+ (for local packaging, if needed)
- (Optional) AWS SAM CLI for simplified deployment
- GitHub repository: [johnwbyrd/pennyworth](https://github.com/johnwbyrd/pennyworth.git)
- Route 53 hosted zone for your domain (e.g., uproro.com) in **us-west-2**

## Secure CI/CD with GitHub Actions OIDC (Recommended)

### 1. Create a Custom IAM Policy for Deployment
- Go to the IAM Console → Policies → Create policy.
- Use the JSON editor to paste a policy with all permissions needed for deployment (see example below).
- Name the policy `pennyworth-deployment`.
- Create the policy.

**Important Security Note:**
- The `iam:PassRole` permission should **not** use a wildcard (`"Resource": "*"`) in production. This is overly permissive and a security risk.
- Instead, restrict `iam:PassRole` to only the specific IAM roles that will be passed to AWS services (such as Lambda execution roles).
- If you do not know the role ARNs yet (e.g., before your first deploy), you may use a wildcard temporarily for development, but **you must update the policy to use specific ARNs before production**.
- You may need to deploy your SAM stack once to get the actual role names/ARNs (these can be exported as outputs from your SAM template), then update your policy.

**Example of a restricted PassRole statement:**
```json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": [
    "arn:aws:iam::<AWS_ACCOUNT_ID>:role/pennyworth-lambda-execution-role"
  ]
}
```
- Optionally, you can further restrict which services the role can be passed to:
```json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "arn:aws:iam::<AWS_ACCOUNT_ID>:role/pennyworth-lambda-execution-role",
  "Condition": {
    "StringEquals": {
      "iam:PassedToService": "lambda.amazonaws.com"
    }
  }
}
```

**Example Policy (for initial development only):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "cognito-idp:*",
        "cognito-identity:*",
        "dynamodb:*",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:ListRoles",
        "iam:ListRolePolicies",
        "iam:GetPolicy",
        "iam:ListPolicies",
        "iam:CreatePolicy",
        "iam:DeletePolicy",
        "iam:UpdateAssumeRolePolicy",
        "logs:*",
        "lambda:*",
        "apigateway:*",
        "s3:*"
      ],
      "Resource": "*"
    }
  ]
}
```
- **Replace the wildcard in `iam:PassRole` with specific ARNs as soon as you know them.**

### 2. Create an IAM Role for GitHub OIDC
- Go to the AWS IAM Console → Roles → Create role
- Select **Web identity** as the trusted entity type
- Choose **OIDC provider**: `token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`
- Attach a trust policy like:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:sub": "repo:johnwbyrd/pennyworth:ref:refs/heads/main"
        }
      }
    }
  ]
}
```
- **Note:** The project/repo name (`johnwbyrd/pennyworth`) is hard-coded here for security. This ensures only workflows from your `main` branch in the `johnwbyrd/pennyworth` repo can assume the role. **This is the only place the project name should be hard-coded.**
- **Attach the custom policy you created in the previous step** (`pennyworth-deployment`) to this role during or after creation.
- **Name this role `pennyworth-github-deploy-role`. Use this name for all references to the deployment role.**

### 3. Attach Least-Privilege Policies
- Attach a policy that allows only the actions needed for deployment (CloudFormation, Lambda, API Gateway, Route 53, ACM, etc.).
- These least-privilege policies should be attached to the `pennyworth-github-deploy-role` IAM role you created in the previous step. This ensures that only this role, when assumed by GitHub Actions, has the necessary permissions to deploy and manage your infrastructure.
- Example (very minimal, expand as needed):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": [
      "cloudformation:*", "lambda:*", "apigateway:*", "dynamodb:*", "acm:*", "route53:*", "iam:PassRole", "logs:*"
    ], "Resource": "*" }
  ]
}
```
- For production, scope resources and actions as tightly as possible.

### 4. Get the Role ARN and Add It to GitHub
- After creating the role, copy its **Role ARN** (e.g., `arn:aws:iam::123456789012:role/pennyworth-github-deploy-role`)
- In your GitHub repository, go to **Settings → Secrets and variables → Actions**
- Add a new **Repository Secret**:
  - Name: `AWS_DEPLOY_ROLE_ARN`
  - Value: (paste the full Role ARN)
- Add a new **Repository Secret**:
  - Name: `ROUTE53_HOSTED_ZONE_ID`
  - Value: (the Route 53 Hosted Zone ID for your base domain, e.g., `Z1234567890ABC`)
- Add a new **Repository Secret**:
  - Name: `STACK_NAME`
  - Value: (your chosen stack name, e.g., `uproro-prod`)
- Add a new **Repository Secret**:
  - Name: `AWS_REGION`
  - Value: (your deployment region, e.g., `us-west-2`)
- Add a new **Repository Secret**:
  - Name: `BASE_DOMAIN`
  - Value: (your base domain, e.g., `uproro.com`)

> **Note:** All deployment configuration values are set as repository secrets for maximum security and to avoid accidental exposure. Do not use repository variables for these values.

### 5. Configure GitHub Actions to Use the Deploy Role
- In your workflow YAML, use the `aws-actions/configure-aws-credentials` action with `role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}`.
- Set the stack name, region, base domain, and hosted zone ID from repository secrets `${{ secrets.STACK_NAME }}`, `${{ secrets.AWS_REGION }}`, `${{ secrets.BASE_DOMAIN }}`, and `${{ secrets.ROUTE53_HOSTED_ZONE_ID }}`.
- **All other configuration (stack name, resource names, etc.) should use secrets or parameters, not hard-coded project names or repository variables.**

> **Note:** The full GitHub Actions workflow YAML for deployment is located at `.github/workflows/deploy.yml`. Please refer to that file for the latest pipeline configuration and environment variable usage.

### 6. Route 53 and Custom Domain Setup
- Your SAM/CloudFormation template should:
  - Create an API Gateway custom domain for `api.${BASE_DOMAIN}` in **us-west-2**
  - Request or reference an ACM certificate for the domain in **us-west-2**
  - Create/update a Route 53 record to point `api.${BASE_DOMAIN}` to the API Gateway custom domain
- You may need a Lambda-backed custom resource or post-deploy script for DNS if not handled natively by SAM

### 7. Best Practices for Long-Term Security
- **Always use OIDC for CI/CD automation**—never static AWS keys
- **Scope IAM roles tightly** (least privilege, restrict to your repo/branch)
- **Rotate and audit roles regularly**
- **Monitor CloudTrail for suspicious activity**
- **Set up alerts for failed or unexpected deployments**

## (Legacy) Static AWS Keys (Not Recommended)
- If you must use static keys, store them in GitHub Secrets as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, and use the same workflow as above (but this is not recommended for production). Always set `aws-region: us-west-2`.

## Deployment Steps (Summary)
1. Set up OIDC IAM role and policies in AWS (in **us-west-2**), hard-coding the project/repo name only in the trust policy
2. Get the role ARN and add it to GitHub as `AWS_DEPLOY_ROLE_ARN`
3. Configure your GitHub Actions workflow to use OIDC and `aws-region: us-west-2`
4. Build and deploy with SAM (or your chosen tool) to **us-west-2** using a stack name derived from your base domain
5. Ensure Route 53 and API Gateway custom domain are set up in **us-west-2**
6. Monitor deployment and logs in AWS Console

## Deployment Steps

### 1. Prepare LiteLLM for Lambda
- Download or clone the [LiteLLM repository](https://github.com/BerriAI/litellm)
- Configure `litellm` with your desired model providers (Bedrock, OpenAI, etc.) in a config file or environment variables
- Ensure all dependencies are included in your deployment package (use Lambda layers or bundle with the function)

### 2. Package the Lambda Function
- Package LiteLLM and its dependencies as a Lambda deployment package (zip or container image)
- Ensure the handler is compatible with Lambda's Node.js runtime
- (Optional) Use a Lambda layer for large dependencies

### 3. Deploy to AWS Lambda
- Create a new Lambda function (Node.js 18.x)
- Upload the deployment package or specify the container image
- Set environment variables for model provider credentials, API keys, and configuration
- Set the timeout to the maximum (15 minutes) to support long-running requests
- Allocate sufficient memory (512MB–1GB recommended for LLM workloads)

### 4. Set Up API Gateway
- Create a new HTTP API or REST API in API Gateway
- Configure routes to forward all requests to the Lambda function
- Enable Lambda response streaming for real-time outputs
- Set payload size limits (max 6 MB for synchronous requests)
- Configure CORS as needed for client integrations

### 5. (Optional) Use AWS SAM for IaC
- Write a `template.yaml` describing the Lambda function, API Gateway, and permissions
- Deploy with `sam deploy --guided`
- SAM will handle packaging, uploading, and resource creation

### 6. Test the Deployment
- Use `curl` or Postman to send OpenAI-compatible requests to your API Gateway endpoint
- Test with VS Code, Cursor, or other OpenAI API clients
- Verify streaming and large/long-running request handling

### 2a. (After First Deploy) Restrict iam:PassRole to Specific Role ARNs

After your first successful deployment, you should restrict the deployment role's `iam:PassRole` permission to only the specific IAM roles created by your stack (such as Lambda execution roles). This is a one-time manual step unless you add new roles in the future.

**How to do this:**
1. **Add Outputs for Role ARNs in your SAM template:**
   ```yaml
   Outputs:
     MyLambdaRoleArn:
       Description: "Lambda execution role ARN"
       Value: !GetAtt MyLambdaRole.Arn
     # Repeat for each Lambda execution role
   ```
2. **Deploy your stack as usual.**
3. **Retrieve the role ARNs after deployment:**
   ```bash
   aws cloudformation describe-stacks --stack-name <your-stack> --query "Stacks[0].Outputs"
   ```
   This will list all outputs, including the Lambda execution role ARNs.
4. **Update your deployment role's policy:**
   - Replace the wildcard in the `iam:PassRole` statement with the specific ARNs you retrieved.
   - Example:
     ```json
     {
       "Effect": "Allow",
       "Action": "iam:PassRole",
       "Resource": [
         "arn:aws:iam::<AWS_ACCOUNT_ID>:role/pennyworth-lambda-execution-role"
       ]
     }
     ```
5. **If you add new Lambda functions (and thus new roles) in the future, repeat this process.**

**Why is this necessary?**
- The deployment role's permissions must be set before you deploy, but the ARNs of the roles you need to reference don't exist until after the stack is deployed. This is a security best practice and a limitation of how AWS separates permissions and resource creation.

## Special Considerations

### Long-Running Requests
- Set Lambda timeout to 15 minutes
- Use response streaming to keep the connection alive and deliver partial results
- If a request nears the timeout, return a partial result with a warning

### Large Inputs/Outputs
- API Gateway limits payloads to 6 MB (synchronous)
- For larger inputs, require clients to upload data to S3 and pass a reference
- For large outputs, stream results in chunks; if output exceeds limits, return a partial result and a warning

### Environment Variables
- `LITELLM_MODEL_PROVIDER` (e.g., bedrock, openai)
- `LITELLM_API_KEYS` (comma-separated list or DynamoDB integration)
- Provider-specific credentials (e.g., AWS, OpenAI)
- Any custom configuration for usage tracking, logging, etc.

## Maintenance
- Monitor Lambda and API Gateway logs in CloudWatch
- Rotate API keys and credentials as needed
- Update the deployment package to add new models or providers

---

This deployment approach ensures a cost-effective, scalable, and secure OpenAI-compatible API proxy, ready for integration with modern developer tools and production-grade CI/CD, all deployed in **us-west-2**. The only place the project name is hard-coded is in the OIDC trust policy for security. 

> **Note:** `ROUTE53_HOSTED_ZONE_ID` is required so that the deployment can create or update DNS records for your API Gateway custom domain. This value is specific to your AWS account and domain, and is not easily or reliably derived from the base domain alone in a cross-account or multi-zone environment. While it is technically possible to look up the hosted zone ID from the base domain using the AWS CLI or SDK, providing it explicitly as a secret avoids ambiguity and ensures the deployment targets the correct zone, especially if you have multiple zones with similar names or subdomains. 