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

### 1. Create an IAM Role for GitHub OIDC
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

### 2. Attach Least-Privilege Policies
- Attach a policy that allows only the actions needed for deployment (CloudFormation, Lambda, API Gateway, Route 53, ACM, etc.).
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

### 3. Get the Role ARN and Add It to GitHub
- After creating the role, copy its **Role ARN** (e.g., `arn:aws:iam::123456789012:role/github-oidc-deploy-role`)
- In your GitHub repository, go to **Settings → Secrets and variables → Actions**
- Add a new **Repository Secret** or **Variable**:
  - Name: `AWS_DEPLOY_ROLE_ARN`
  - Value: (paste the full Role ARN)

### 4. Configure GitHub Actions to Use the Deploy Role
- In your workflow YAML, use the `aws-actions/configure-aws-credentials` action with `role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}` (or `${{ vars.AWS_DEPLOY_ROLE_ARN }}` if you use a variable):
- Set the stack name dynamically from the base domain (e.g., `uproro-prod` if `BASE_DOMAIN` is `uproro.com`).
- **All other configuration (stack name, resource names, etc.) should use variables or parameters, not hard-coded project names.**

```yaml
env:
  AWS_REGION: ${{ vars.AWS_REGION }}
  BASE_DOMAIN: ${{ vars.BASE_DOMAIN }}
  ROUTE53_HOSTED_ZONE_ID: ${{ secrets.ROUTE53_HOSTED_ZONE_ID }}
  AWS_DEPLOY_ROLE_ARN: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
  STACK_NAME: ${{ format('{0}-prod', env.BASE_DOMAIN != null && env.BASE_DOMAIN != '' && contains(env.BASE_DOMAIN, '.') ? split(env.BASE_DOMAIN, '.')[0] : 'app') }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ env.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}
          role-session-name: github-actions
      - name: Build and package Lambda
        run: sam build
      - name: Set stack name
        id: stackname
        run: |
          BASE="${BASE_DOMAIN%%.*}"
          echo "STACK_NAME=${BASE}-prod" >> $GITHUB_ENV
      - name: Deploy with SAM
        run: |
          sam deploy --stack-name $STACK_NAME \
            --capabilities CAPABILITY_IAM \
            --region $AWS_REGION \
            --parameter-overrides \
              DomainName=api.${BASE_DOMAIN} \
              HostedZoneId=$ROUTE53_HOSTED_ZONE_ID
```

**Instructions:**
- The `STACK_NAME` is set dynamically based on the base domain (e.g., `uproro-prod` for `uproro.com`).
- The `Set stack name` step extracts the part before the first dot in `BASE_DOMAIN` and appends `-prod`.
- The `sam deploy` command uses this dynamic stack name.
- **Do not hard-code the project name anywhere except the OIDC trust policy.**

### 5. Route 53 and Custom Domain Setup
- Your SAM/CloudFormation template should:
  - Create an API Gateway custom domain for `api.${BASE_DOMAIN}` in **us-west-2**
  - Request or reference an ACM certificate for the domain in **us-west-2**
  - Create/update a Route 53 record to point `api.${BASE_DOMAIN}` to the API Gateway custom domain
- You may need a Lambda-backed custom resource or post-deploy script for DNS if not handled natively by SAM

### 6. Best Practices for Long-Term Security
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