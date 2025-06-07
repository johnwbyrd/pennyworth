def protected_handler():
    import os
    return {
        "ApiKeysTableName": os.environ["API_KEYS_TABLE"]
    }, 200 