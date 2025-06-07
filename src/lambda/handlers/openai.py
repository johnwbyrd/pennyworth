from model_router import get_model_config
import litellm
from utils import logger

def list_models_handler():
    try:
        model_list = [
            {"id": k, **v}
            for k, v in get_model_config.__globals__["model_map"].items()
        ]
        return {"data": model_list}, 200
    except Exception as e:
        logger.error(f"Error in models: {e}")
        return {"error": str(e)}, 500

def chat_completions_handler(body):
    model_name = body.get("model")
    messages = body.get("messages")
    if not model_name or not messages:
        return {"error": "Missing 'model' or 'messages' in request body."}, 400
    try:
        model_config = get_model_config(model_name)
        response = litellm.completion(
            model=model_config["model_id"],
            messages=messages,
            provider=model_config["provider"],
            aws_region=None
        )
        return response, 200
    except Exception as e:
        logger.error(f"Error in chat/completions: {e}")
        return {"error": str(e)}, 500

def completions_handler(body):
    model_name = body.get("model")
    prompt = body.get("prompt")
    if not model_name or not prompt:
        return {"error": "Missing 'model' or 'prompt' in request body."}, 400
    try:
        model_config = get_model_config(model_name)
        response = litellm.completion(
            model=model_config["model_id"],
            prompt=prompt,
            provider=model_config["provider"],
            aws_region=None
        )
        return response, 200
    except Exception as e:
        logger.error(f"Error in completions: {e}")
        return {"error": str(e)}, 500

def embeddings_handler(body):
    model_name = body.get("model")
    input_data = body.get("input")
    if not model_name or input_data is None:
        return {"error": "Missing 'model' or 'input' in request body."}, 400
    try:
        model_config = get_model_config(model_name)
        response = litellm.embeddings(
            model=model_config["model_id"],
            input=input_data,
            provider=model_config["provider"],
            aws_region=None
        )
        return response, 200
    except Exception as e:
        logger.error(f"Error in embeddings: {e}")
        return {"error": str(e)}, 500 