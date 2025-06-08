# TODO (Short-Term)

## API & Lambda
- Implement all user management endpoints (get, update, delete, list users)
- Implement all API key management endpoints (status, rotate, revoke)
- Complete MCP protocol support and test with VS Code/Cursor
- Add/expand unit and integration tests for all handler modules
- Implement a test suite using Postman and pytest
- Review and improve error handling and response consistency

## Security & IAM
- Review Cognito group/role mappings and permissions
- Audit IAM roles and policies for least privilege
- Add/verify MFA enforcement for admin users in Cognito

## Observability
- Review X-Ray traces for all critical paths
- Add custom CloudWatch metrics/alarms for key endpoints

## CI/CD & Deployment
- Add deployment status badge to README
- Review and document environment variable usage
- Add pre-deploy and post-deploy sanity checks to GitHub Actions

## Documentation
- Update or add endpoint documentation for all REST APIs
- Add quickstart guide for new developers
- Review and update cost analysis in doc/cost.md

## Miscellaneous
- Clean up any unused files or legacy references in the repo
- Review and update TODOs in code comments 