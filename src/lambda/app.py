import json
import litellm
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Placeholder: configure LiteLLM to use AWS Bedrock
# You will need to set environment variables or pass config for your Bedrock provider/model
# Example: litellm.provider = "bedrock"
#          litellm.bedrock_model = "your-model-id"

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    try:
        if event.get("httpMethod") == "GET":
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "pennyworth is running."})
            }

        body = json.loads(event.get("body") or "{}")
        prompt = body.get("prompt")
        if not prompt:
            logger.warning("Missing 'prompt' in request body: %s", body)
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'prompt' in request body."})
            }

        # Call Bedrock via LiteLLM (update model/provider as needed)
        # Example: response = litellm.completion("your-model-id", prompt=prompt)
        # For now, we'll use a placeholder response
        response = {
            "choices": [
                {"text": f"Echo: {prompt}"}
            ]
        }
        logger.info("Returning response: %s", json.dumps(response))
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
    except Exception as e:
        logger.exception("Error in Lambda handler")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        } 