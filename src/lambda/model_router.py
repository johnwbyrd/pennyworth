# Model router for mapping friendly model names to Bedrock model IDs

def get_model_config(model_name):
    """
    Map a friendly model name to Bedrock model/provider config.
    Extend this mapping as new models/providers are added.
    """
    model_map = {
        "claude-instant": {
            "provider": "bedrock",
            "model_id": "anthropic.claude-instant-v1"
        },
        "claude-v2": {
            "provider": "bedrock",
            "model_id": "anthropic.claude-v2"
        },
        "titan-text": {
            "provider": "bedrock",
            "model_id": "amazon.titan-text-lite-v1"
        },
        # Add more models here as needed
    }
    if model_name not in model_map:
        raise ValueError(f"Model '{model_name}' is not supported.")
    return model_map[model_name] 