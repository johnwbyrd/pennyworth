# Deployment Guide

## Overview
This guide describes how to deploy **Pennyworth** (the LiteLLM-based OpenAI-compatible API proxy) on AWS Lambda, with API Gateway as the HTTP entry point. It covers environment setup, CI/CD, permissions, and best practices for secure, zero-cost-at-rest, production-grade deployment.

## Prerequisites
- AWS account with access to Lambda, API Gateway, Route 53, ACM, DynamoDB, Bedrock, and IAM in **us-west-2**
- AWS CLI configured (for initial setup)
- Node.js 18+ (for local packaging, if needed)
- (Optional) AWS SAM CLI for infrastructure-as-code
- GitHub repository: [johnwbyrd/pennyworth](https://github.com/johnwbyrd/pennyworth.git)
- Route 53 hosted zone for your domain (e.g., `uproro.com`) in **us-west-2**

## CI/CD with GitHub Actions and OIDC

### 1. Create a Custom IAM Policy for Deployment

- In the IAM Console, create a policy named `pennyworth-deployment`.
- This policy should grant only the permissions required for deployment and management of the stack.
- **For development**, you may use a broad policy (see below), but for **production**, restrict actions and resources as tightly as possible.

#### Example: Development Policy (for bootstrapping only)

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
        "iam:TagRole",
        "iam:UntagRole",
        "iam:CreateServiceLinkedRole",
        "logs:*",
        "lambda:*",
        "apigateway:*",
        "s3:*",
        "route53:GetHostedZone",
        "route53:ListHostedZones",
        "route53:ChangeResourceRecordSets",
        "route53:GetChange",
        "route53:ListResourceRecordSets",
        "acm:DescribeCertificate",
        "acm:ListCertificates",
        "acm:GetCertificate",
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

- **Note:** This policy is intentionally broad for initial setup. **Do not use in production.**

### 2. Create the GitHub OIDC Deployment Role

- In IAM, create a role named `pennyworth-github-deploy-role`.
- Trusted entity: OIDC provider `token.actions.githubusercontent.com`
- Trust policy should restrict to your repo and branch:

```json
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
```

- Attach the `pennyworth-deployment` policy to this role.

## Permissions Reference

### Development Permissions

- Use the **Development Policy** above for initial stack creation and troubleshooting.
- This policy allows full management of all required AWS resources, but should be replaced with a production policy as soon as possible.

### Production Permissions

#### 1. **Lambda Execution Role (API Runtime)**

This role is assumed by your deployed Lambda functions. It should have the minimum permissions required for runtime operation.

**Required permissions:**

```json
[
  {
    "Effect": "Allow",
    "Action": [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ],
    "Resource": "arn:aws:dynamodb:us-west-2:<ACCOUNT_ID>:table/pennyworth-apikeys"
  },
  {
    "Effect": "Allow",
    "Action": [
      "bedrock:InvokeModel"
    ],
    "Resource": "*"
  },
  {
    "Effect": "Allow",
    "Action": [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:us-west-2:<ACCOUNT_ID>:log-group:/aws/lambda/pennyworth*"
  }
  // Add KMS and X-Ray permissions if needed
]
```

#### 2. **GitHub Actions Deployment Role**

This role is assumed by GitHub Actions for deploying with SAM. It needs permissions to create, update, and delete all stack resources.

**Required permissions:**

```json
[
  {
    "Effect": "Allow",
    "Action": [
      "cloudformation:*",
      "lambda:*",
      "apigateway:*",
      "dynamodb:*",
      "acm:DescribeCertificate",
      "acm:ListCertificates",
      "acm:GetCertificate",
      "route53:GetHostedZone",
      "route53:ListHostedZones",
      "route53:ChangeResourceRecordSets",
      "route53:GetChange",
      "route53:ListResourceRecordSets",
      "logs:*",
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
      "iam:TagRole",
      "iam:UntagRole",
      "iam:CreateServiceLinkedRole",
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ],
    "Resource": "*"
  }
]
```

- **Restrict `iam:PassRole` to only the Lambda execution roles created by your stack.**
- After your first deploy, update the policy to use specific ARNs for `iam:PassRole` and other resources.

## GitHub Secrets

Add the following repository secrets:

- `AWS_DEPLOY_ROLE_ARN`: The ARN of your deployment role
- `ROUTE53_HOSTED_ZONE_ID`: Your Route 53 hosted zone ID
- `STACK_NAME`: Your CloudFormation/SAM stack name
- `AWS_REGION`: Deployment region (e.g., `us-west-2`)
- `BASE_DOMAIN`: Your base domain (e.g., `uproro.com`)

## GitHub Actions Workflow

- The deployment workflow is defined in `.github/workflows/deploy.yml`.
- It uses OIDC to assume the deployment role and deploys using SAM.
- All configuration is passed via secrets.

## Route 53 and Custom Domain Setup

- The SAM/CloudFormation template should:
  - Create an API Gateway custom domain for `api.${BASE_DOMAIN}` in **us-west-2**
  - Reference an ACM certificate for the domain in **us-west-2**
  - Create/update a Route 53 record to point `api.${BASE_DOMAIN}` to the API Gateway custom domain

## Best Practices

- **Always use OIDC for CI/CD automation**—never static AWS keys
- **Scope IAM roles tightly** (least privilege, restrict to your repo/branch)
- **Rotate and audit roles regularly**
- **Monitor CloudTrail for suspicious activity**
- **Set up alerts for failed or unexpected deployments**

## After First Deploy: Restrict `iam:PassRole`

- After your first deployment, retrieve the ARNs of the Lambda execution roles from stack outputs.
- Update the deployment policy to restrict `iam:PassRole` to only those ARNs.

## Maintenance

- Monitor Lambda and API Gateway logs in CloudWatch
- Rotate API keys and credentials as needed
- Update the deployment package to add new models or providers

## Appendix: ACM Certificate and DNS

- Create an ACM certificate for your custom domain in **us-west-2**
- Reference the certificate ARN in your SAM template
- Use Route 53 to point your custom domain to the API Gateway domain

**This guide is kept up to date with all permissions and deployment best practices as the project evolves.**