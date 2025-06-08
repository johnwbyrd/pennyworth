# Architecture Overview

## Purpose
This project provides an OpenAI-compatible API proxy, powered by [LiteLLM](https://github.com/BerriAI/litellm), hosted on AWS Lambda. It is designed to:
- Enable multiple LLMs (e.g., Bedrock, OpenAI, Azure) for code editing and chat in developer tools (VS Code, Cursor, etc.)
- Maintain zero-cost-at-rest by using serverless infrastructure
- Support long-running and large requests within Lambda's constraints

## High-Level Architecture

- **API Gateway**: Receives HTTP requests from clients (OpenAI API or MCP protocol)
- **AWS Lambda (LiteLLM)**: Handles all API logic, model routing, and authentication
- **Cognito (required)**: Stores users and API keys as custom attributes. **API key management is exclusively via Cognito custom attributes and REST API endpoints; LiteLLM's built-in key management is not used.**
- **CloudWatch**: Logging and metrics

## Key Design Principles

- **OpenAI API Compatibility**: All endpoints and request/response formats match OpenAI's API, enabling drop-in use with existing clients.
- **Multi-LLM Support**: LiteLLM routes requests to AWS Bedrock, OpenAI, or other providers based on configuration.
- **Serverless/Zero-Cost-At-Rest**: No compute costs when idle; all resources are on-demand.
- **Simple Auth**: API key authentication (managed by Cognito custom attributes and the REST API; do not use LiteLLM's built-in key management).

## Handling Long-Running and Large Requests

### Lambda Constraints
- **Max execution time**: 15 minutes
- **Max payload size**: 6 MB (synchronous), 256 KB (event payload)
- **Streaming**: Lambda response streaming allows for real-time, long-running responses (up to 15 minutes)

### Strategies
- **Streaming Responses**: For chat/completions, use Lambda response streaming to send partial results as they are generated. This supports long outputs and keeps connections alive for up to 15 minutes.
- **Chunked Input Handling**: For large inputs, clients should send data in chunks or reference S3 objects (if needed). The API should reject requests that exceed Lambda's payload limits with a clear error message.
- **Large Output Handling**: Outputs are streamed in chunks. If a response would exceed Lambda's memory or time limits, the API returns a partial result and a clear error/warning.
- **Timeout Management**: If a model call risks exceeding Lambda's timeout, the proxy should terminate gracefully and return a partial result with a timeout notice.

## Rationale for This Architecture
- **Simplicity**: LiteLLM handles most API logic, reducing custom code.
- **Scalability**: Lambda scales automatically with demand.
- **Cost Efficiency**: No cost when not in use; pay only for what you use.
- **Compatibility**: Works with any OpenAI-compatible client, including VS Code and Cursor.
- **Extensibility**: Easy to add new LLM providers or custom logic as needed.

## Optional Extensions
- **MCP Protocol Support**: If required, a thin Lambda or container can be added to handle MCP endpoints and route to LiteLLM or directly to LLMs. **(Note: MCP support is now a near-term requirement, not just optional.)**
- **Custom Usage Tracking**: Use CloudWatch or other stores for per-user/model usage and cost tracking.
- **API Key Management**: Use Cognito custom attributes for API key storage, or rely on LiteLLM's built-in support (not recommended).

---

This architecture is designed to be robust, cost-effective, and easy to maintain, while supporting advanced use cases for developer productivity tools. 

**A Python CLI tool is used for API key creation, auditing, and revocation, and only shows the key once at creation. All key management is performed via REST API endpoints.** 