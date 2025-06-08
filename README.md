# pennyworth

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Build Status](https://github.com/johnwbyrd/pennyworth/actions/workflows/deploy.yml/badge.svg)](https://github.com/johnwbyrd/pennyworth/actions)
[![AWS Ready](https://img.shields.io/badge/AWS-Ready-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![AWS SAM](https://img.shields.io/badge/AWS-SAM-blue?logo=amazon-aws)](https://aws.amazon.com/serverless/sam/)

[//]: # (SPDX-License-Identifier: AGPL-3.0-only)

**pennyworth** is all the LLMs, for cheap people.

**pennyworth** is a prototype for a secure, serverless API proxy infrastructure-as-code (IaC) designed to make the latest large language models -- such as AWS Bedrock and others -- available through a single, OpenAI-compatible interface. The project is built for individuals and teams of programmers or other users who want to access modern LLMs from one convenient API endpoint, whether for code editing, chat, or other AI-powered workflows.

At the heart of pennyworth is a zero-cost-at-rest philosophy: when the system is not in use, it incurs no compute cost. This is achieved by leveraging AWS serverless technologies -- Lambda, API Gateway, and Route 53 -- so you only pay for what you use. This infrastructure-as-code is fully automated, with GitHub Actions deploying via AWS SAM and secure, keyless OIDC. Custom domains and TLS are handled through Route 53 and ACM, making it easy to deploy a branded, secure endpoint for your team or organization.

Security and cost-awareness are core to the design. API keys are managed securely (hashed, never stored in plaintext), IAM roles are set up for least privilege.  All configuration is handled through environment variables and secrets: never hard-coded.  The system is designed to be extensible, so you can add new LLM providers as they become available, and to support both individual and team usage with per-user or per-key cost tracking and reporting.

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

### Human-Readable AGPL 3.0 Summary

- **You are free to use, modify, and share this code** as long as you comply with the AGPL 3.0 license.
- **If you modify this code and run it as a service (including over a network), you must also make your modified source code available under the AGPL 3.0.**
- **Closed-source forks and proprietary versions of this project are not permitted.**
- **Selling a closed-source or proprietary service based on this code is outside the scope of this license and is not allowed.**
- **If you build a service or product using this code, you must provide your users with access to the complete, corresponding source code under the same AGPL 3.0 license.**
- For more information, see the [GNU AGPL v3.0 FAQ](https://www.gnu.org/licenses/agpl-3.0-faq.html). 