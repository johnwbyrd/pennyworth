# Authentication helpers for API key validation

def validate_api_key(api_key):
    """
    Validate the given API key by hashing and looking up in DynamoDB.
    Returns metadata if valid, raises error if not.
    """
    # TODO: Implement DynamoDB hash lookup and status check
    raise NotImplementedError("API key validation not implemented yet.") 