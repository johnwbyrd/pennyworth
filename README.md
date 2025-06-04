# pennyworth

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Build Status](https://github.com/<your-org-or-username>/pennyworth/actions/workflows/deploy.yml/badge.svg)](https://github.com/<your-org-or-username>/pennyworth/actions)
[![AWS Ready](https://img.shields.io/badge/AWS-Ready-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![AWS SAM](https://img.shields.io/badge/AWS-SAM-blue?logo=amazon-aws)](https://aws.amazon.com/serverless/sam/)

[//]: # (SPDX-License-Identifier: AGPL-3.0-only)

**pennyworth** is a secure, serverless API proxy designed to make the latest large language models—such as AWS Bedrock and others—available through a single, OpenAI-compatible interface. The project is built for individuals and teams of programmers or other users who want to access modern LLMs from one convenient API endpoint, whether for code editing, chat, or other AI-powered workflows.

At the heart of pennyworth is a zero-cost-at-rest philosophy: when the system is not in use, it incurs no compute cost. This is achieved by leveraging AWS serverless technologies—Lambda, API Gateway, DynamoDB, and Route 53—so you only pay for what you use. The infrastructure is fully automated and managed via AWS SAM and GitHub Actions, with secure, keyless CI/CD using OIDC. Custom domains and TLS are handled through Route 53 and ACM, making it easy to deploy a branded, secure endpoint for your team or organization.

Security and cost-awareness are core to the design. API keys are managed securely (hashed, never stored in plaintext), IAM roles are set up for least privilege, and all configuration is handled through environment variables and secrets—never hard-coded. The system is designed to be extensible, so you can add new LLM providers as they become available, and to support both individual and team usage with per-user or per-key cost tracking and reporting.

Whether you're a solo developer, a small team, or an organization looking to provide modern LLM access to your users, pennyworth offers a robust, maintainable, and future-proof foundation. For full details on architecture, deployment, security, and usage, see the documentation below.

For detailed documentation, see:

- [Project Plan](doc/plan.md)
- [Deployment Guide](doc/deployment.md)
- [System Overview](doc/overview.md)
- [Architecture](doc/architecture.md)
- [Security Guide](doc/security.md)
- [Cost Analysis](doc/cost.md)
- [CLI Tool Design](doc/cli-tool.md)
- [CLI Tool Authentication & Permissions](doc/cli-tool-auth.md)

---

## License

This project is licensed under the GNU Affero General Public License v3.0 only. See [LICENSE](LICENSE) for details. 