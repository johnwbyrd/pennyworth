# Resource Tagging Strategy

## Overview
Pennyworth uses a consistent tagging strategy across all AWS resources to enable:
- Resource organization and discovery
- Cost allocation and tracking
- Access control
- Automation and maintenance
- Environment management
- Stack-level resource grouping

## Standard Tags

All resources are tagged with the following standard tags:

| Tag Key | Description | Example Values |
|---------|-------------|----------------|
| `Project` | Project identifier | `Pennyworth` |
| `Environment` | Deployment environment | `dev`, `prod` |
| `StackName` | CloudFormation stack identifier | `pennyworth-dev`, `pennyworth-prod` |
| `Component` | Functional component | See Component Tags below |

## Component Tags

Resources are tagged with a `Component` tag to identify their functional role:

| Component Value | Description | Example Resources |
|-----------------|-------------|-------------------|
| `Authentication` | User authentication and authorization | Cognito User Pool, Identity Pool, IAM Roles |
| `APIKeys` | API key management | DynamoDB Table |
| `APIProxy` | API proxy functionality | Lambda Function |
| `Logging` | Logging and monitoring | CloudWatch Log Groups |
| `API` | API Gateway resources | Custom Domain, Base Path Mapping |

## Tagging Examples

### Authentication Resources
```yaml
Tags:
  - Key: Project
    Value: Pennyworth
  - Key: Environment
    Value: !Ref Environment
  - Key: StackName
    Value: !Ref AWS::StackName
  - Key: Component
    Value: Authentication
```

### API Key Resources
```yaml
Tags:
  - Key: Project
    Value: Pennyworth
  - Key: Environment
    Value: !Ref Environment
  - Key: StackName
    Value: !Ref AWS::StackName
  - Key: Component
    Value: APIKeys
```

### API Proxy Resources
```yaml
Tags:
  Project: Pennyworth
  Environment: !Ref Environment
  StackName: !Ref AWS::StackName
  Component: APIProxy
```

## Tag Usage

### Cost Allocation
- Use `Project` and `Environment` tags for cost allocation reports
- Track costs by component using the `Component` tag
- Group costs by stack using the `StackName` tag

### Resource Discovery
- Find all resources for a specific environment: `Environment=dev`
- Find all authentication resources: `Component=Authentication`
- Find all resources for the project: `Project=Pennyworth`
- Find all resources in a specific stack: `StackName=pennyworth-dev`

### Access Control
- Use tags in IAM policies for fine-grained access control
- Example: Allow access only to dev environment resources
- Example: Restrict access to specific stack resources

### Automation
- Use tags for automated maintenance tasks
- Example: Set log retention based on environment
- Example: Perform stack-specific operations using `StackName`

## Best Practices

1. **Consistency**
   - Always use the standard tag set
   - Use consistent casing and values
   - Apply tags to all resources
   - Use `!Ref AWS::StackName` for stack name consistency

2. **Automation**
   - Apply tags through infrastructure as code
   - Validate tag presence in CI/CD
   - Use stack name in automated operations

3. **Documentation**
   - Keep this document updated
   - Document any new component types
   - Include tagging in resource creation procedures
   - Document stack naming conventions

4. **Validation**
   - Verify tags are applied correctly
   - Check for missing or incorrect tags
   - Monitor tag compliance
   - Validate stack name consistency

## Adding New Components

When adding new resources:

1. Identify the appropriate component type
2. Apply all standard tags
3. Update this documentation if adding a new component type
4. Ensure consistent tag application across similar resources
5. Include stack name in all resource tags

## Tag Management

### Adding Tags
- Add tags through CloudFormation/SAM templates
- Use consistent tag structure
- Include tags in all resource definitions
- Always include stack name using `!Ref AWS::StackName`

### Updating Tags
- Update tags through infrastructure as code
- Maintain tag consistency across updates
- Document any tag changes
- Preserve stack name references

### Removing Tags
- Remove tags through infrastructure as code
- Update documentation accordingly
- Maintain tag consistency
- Consider stack name dependencies

## Compliance and Governance

- Tags are mandatory for all resources
- Tag values must follow the defined standards
- Regular audits of tag compliance
- Automated tag validation in CI/CD
- Stack name consistency checks

## Stack Naming Convention

The `StackName` tag should follow this convention:
- Format: `pennyworth-{environment}`
- Example: `pennyworth-dev`, `pennyworth-prod`
- Use lowercase with hyphens
- Keep names concise but descriptive

---

This tagging strategy ensures consistent resource organization and enables effective management of the Pennyworth infrastructure across multiple environments and stacks. 