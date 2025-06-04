# Deployment Guide

## Overview
This guide describes how to deploy **Pennyworth** (the LiteLLM-based OpenAI-compatible API proxy) on AWS Lambda, with API Gateway as the HTTP entry point. It covers environment setup, CI/CD, permissions, and best practices for secure, zero-cost-at-rest, production-grade deployment.

## Prerequisites
- AWS account with access to Lambda, API Gateway, Route 53, ACM, DynamoDB, Bedrock, and IAM in your chosen region
- AWS CLI configured (for initial setup)
- Node.js 18+ (for local packaging, if needed)
- (Optional) AWS SAM CLI for infrastructure-as-code
- A GitHub repository where you can run Actions
- Route 53 hosted zone for your domain (BASE_DOMAIN) in your chosen region

## Required GitHub Repository Secrets

The following secrets **must** be set in your GitHub repository (Settings → Secrets and variables → Actions) for deployment to work. Each is referenced by the deployment workflow and SAM template.

### 1. `AWS_DEPLOY_ROLE_ARN`
- **What:** The ARN of the IAM role that GitHub Actions will assume for deployment (OIDC trust, least-privilege policy attached).
- **How to obtain:**
  - Create an IAM role in AWS with OIDC trust for GitHub Actions (see "CI/CD with GitHub Actions and OIDC" below).
  - Attach the production deployment policy.
  - Copy the role ARN (e.g., `arn:aws:iam::123456789012:role/pennyworth-github-deploy-role`).
- **Format:** `arn:aws:iam::<ACCOUNT_ID>:role/<ROLE_NAME>`

### 2. `AWS_REGION`
- **What:** The AWS region to deploy to (must match all resources, e.g., Lambda, API Gateway, ACM, Route 53, DynamoDB).
- **How to obtain:**
  - Choose your AWS region (e.g., `us-west-2`, `us-east-1`).
- **Format:** AWS region code (e.g., `us-west-2`)

### 3. `BASE_DOMAIN`
- **What:** The base domain for your API (e.g., `example.com`). Used to create the custom API Gateway domain (e.g., `api.example.com`).
- **How to obtain:**
  - Register your domain and set up a Route 53 hosted zone for it.
- **Format:** Domain name (e.g., `example.com`)

### 4. `ROUTE53_HOSTED_ZONE_ID`
- **What:** The ID of your Route 53 hosted zone for `BASE_DOMAIN`.
- **How to obtain:**
  - In AWS Console → Route 53 → Hosted zones, find your domain and copy the Hosted Zone ID (e.g., `Z1234567890ABC`).
- **Format:** Hosted zone ID string (e.g., `Z1234567890ABC`)

### 5. `ACM_CERTIFICATE_ARN`
- **What:** The ARN of the ACM certificate for your custom domain (must be in the same region as API Gateway).
- **How to obtain:**
  - In AWS Console → Certificate Manager (ACM), request or import a certificate for `api.<BASE_DOMAIN>` (DNS validation recommended).
  - After validation, copy the certificate ARN (e.g., `arn:aws:acm:us-west-2:123456789012:certificate/abcdefg-1234-5678-90ab-cdef12345678`).
- **Format:** `arn:aws:acm:<REGION>:<ACCOUNT_ID>:certificate/<UUID>`

### 6. `STACK_NAME`
- **What:** The name of your CloudFormation/SAM stack. Used to group all resources and for stack updates/deletes.
- **How to choose:**
  - Pick a short, unique name (e.g., `pennyworth-prod`, `myteam-llm-api`).
- **Format:** Alphanumeric string, dashes allowed (e.g., `pennyworth-prod`)

---

## Setting Up Repository Secrets

1. Go to your GitHub repository → **Settings → Secrets and variables → Actions**.
2. Click **New repository secret** for each of the above.
3. Paste the value and save. **Do not use repository variables for these values.**

---

## CI/CD with GitHub Actions and OIDC

### 1. Create a Custom IAM Policy for Deployment

- In the IAM Console, create a policy named `pennyworth-deployment`.
- This policy should grant only the permissions required for deployment and management of the stack.
- **For development**, you may use a broad policy (see below), but for **production**, restrict actions and resources as tightly as possible.

## Permissions Reference

### Development Deployment Policy (Bootstrapping/Iteration)

This policy is intentionally broad and should only be used for initial stack creation, troubleshooting, and development. It allows full management of all required AWS resources. **Do not use in production.**

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

---

### Production Deployment Policy (Least-Privilege, Resource-Scoped)

This policy should be used for production deployments. It is tightly scoped to only the actions and resources required for deploying and updating the Pennyworth stack. Replace placeholders (e.g., `<REGION>`, `<ACCOUNT_ID>`, `<STACK_NAME>`, `<BUCKET_NAME>`) with your actual values or use CloudFormation/SAM parameters. Use the secret names (e.g., ACM_CERTIFICATE_ARN, ROUTE53_HOSTED_ZONE_ID) in your workflow and template.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    // CloudFormation: Manage stack resources
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:GetTemplate",
        "cloudformation:ValidateTemplate"
      ],
      "Resource": "*"
    },
    // Lambda: Manage functions created by this stack
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:DeleteFunction",
        "lambda:GetFunction",
        "lambda:ListFunction s",
        "lambda:AddPermission",
        "lambda:RemovePermission"
      ],
      "Resource": "arn:aws:lambda:<REGION>:<ACCOUNT_ID>:function:<STACK_NAME>*"
    },
    // IAM: Only for passing roles created by this stack (e.g., Lambda execution roles)
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole",
        "iam:GetRole",
        "iam:TagRole",
        "iam:UntagRole",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:CreateServiceLinkedRole"
      ],
      "Resource": [
        "arn:aws:iam::<ACCOUNT_ID>:role/<STACK_NAME>*"
      ]
    },
    // DynamoDB: Manage the API key table
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:UpdateTable",
        "dynamodb:DeleteTable",
        "dynamodb:DescribeTable",
        "dynamodb:ListTables"
      ],
      "Resource": "arn:aws:dynamodb:<REGION>:<ACCOUNT_ID>:table/pennyworth-apikeys"
    },
    // API Gateway: Manage APIs created by this stack
    {
      "Effect": "Allow",
      "Action": [
        "apigateway:POST",
        "apigateway:PUT",
        "apigateway:GET",
        "apigateway:DELETE",
        "apigateway:PATCH"
      ],
      "Resource": "*"
    },
    // S3: For deployment artifacts (restrict to deployment bucket)
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::<BUCKET_NAME>",
        "arn:aws:s3:::<BUCKET_NAME>/*"
      ]
    },
    // Route 53: Only for the relevant hosted zone
    {
      "Effect": "Allow",
      "Action": [
        "route53:GetHostedZone",
        "route53:ChangeResourceRecordSets",
        "route53:GetChange",
        "route53:ListResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/${{ secrets.ROUTE53_HOSTED_ZONE_ID }}"
    },
    // ACM: Only for the certificate(s) used by the stack
    {
      "Effect": "Allow",
      "Action": [
        "acm:DescribeCertificate",
        "acm:ListCertificates",
        "acm:GetCertificate"
      ],
      "Resource": "${{ secrets.ACM_CERTIFICATE_ARN }}"
    },
    // CloudWatch Logs: For Lambda and API Gateway logs
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:<REGION>:<ACCOUNT_ID>:log-group:/aws/lambda/<STACK_NAME>*"
    },
    // Bedrock: For model invocation testing (optional, restrict as needed)
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

**Rationale for each permission is provided in comments above.**

## Stack-Based Resource Management

### Resource Tagging Strategy

All resources in the Pennyworth stack are tagged with a consistent set of tags to enable:
- Resource organization and discovery
- Cost allocation and tracking
- Access control
- Automation and maintenance
- Environment management
- Stack-level resource grouping

The standard tag set includes:
- `Project: Pennyworth`
- `Environment: !Ref Environment`
- `StackName: !Ref AWS::StackName`
- `Component: <ComponentType>` (e.g., Authentication, APIKeys, APIProxy)

### Stack-Based IAM Policies

The stack name and tags can be used to create more granular IAM policies that:
1. **Isolate Resources**: Restrict access to resources within specific stacks
2. **Control Cross-Stack Access**: Manage access between different Pennyworth deployments
3. **Enforce Environment Separation**: Prevent accidental modifications to production resources
4. **Enable Component-Level Access**: Grant permissions based on resource components

Example policy patterns:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "dynamodb:*",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:ResourceTag/StackName": "pennyworth-prod",
                    "aws:ResourceTag/Component": "APIKeys"
                }
            }
        }
    ]
}
```

### Best Practices for Stack-Based Access Control

1. **Stack Isolation**
   - Use stack name in resource ARNs
   - Tag all resources with stack name
   - Restrict cross-stack access

2. **Environment Separation**
   - Use environment-specific stack names
   - Enforce strict prod/dev separation
   - Prevent accidental cross-environment access

3. **Component-Based Access**
   - Tag resources by component type
   - Create component-specific policies
   - Enable fine-grained access control

4. **Audit and Compliance**
   - Track resource access by stack
   - Monitor cross-stack operations
   - Maintain access logs

### Implementation Notes

1. **Resource Naming**
   - Use stack name in resource names
   - Follow consistent naming patterns
   - Enable easy resource identification

2. **Policy Management**
   - Create stack-specific policies
   - Use tag-based conditions
   - Regular policy reviews

3. **Access Patterns**
   - Define clear access boundaries
   - Document cross-stack requirements
   - Monitor access patterns

4. **Maintenance**
   - Regular tag audits
   - Policy compliance checks
   - Access pattern reviews

## GitHub Actions Workflow

- The deployment workflow is defined in `.github/workflows/deploy.yml`.
- It uses OIDC to assume the deployment role and deploys using SAM.
- All configuration is passed via secrets.

## Route 53 and Custom Domain Setup

- The SAM/CloudFormation template should:
  - Create an API Gateway custom domain for `api.${BASE_DOMAIN}` in your chosen region
  - Reference an ACM certificate for the domain in your chosen region
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

- Create an ACM certificate for your custom domain in your chosen region
- Reference the certificate ARN in your SAM template
- Use Route 53 to point your custom domain to the API Gateway domain
