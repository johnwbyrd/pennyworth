import json
import logging
from openai import handle_openai_request  # to be implemented
from mcp import handle_mcp_request      # to be implemented

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Placeholder: configure LiteLLM to use AWS Bedrock
# You will need to set environment variables or pass config for your Bedrock provider/model
# Example: litellm.provider = "bedrock"
#          litellm.bedrock_model = "your-model-id"

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    try:
        path = event.get("path") or event.get("requestContext", {}).get("http", {}).get("path", "")
        if path.startswith("/v1/"):
            # Route to OpenAI-compatible handler
            return handle_openai_request(event, context)
        elif path.startswith("/mcp/"):
            # Route to MCP handler
            return handle_mcp_request(event, context)
        elif event.get("httpMethod") == "GET":
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "pennyworth is running."})
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Not found"})
            }
    except Exception as e:
        logger.exception("Error in Lambda handler")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        } 