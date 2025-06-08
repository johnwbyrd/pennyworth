from utils import tracer

@tracer.capture_method
def well_known_handler():
    import os
    return {
        "UserPoolId": os.environ["USER_POOL_ID"],
        "UserPoolClientId": os.environ["USER_POOL_CLIENT_ID"],
        "IdentityPoolId": os.environ["IDENTITY_POOL_ID"],
        "Region": os.environ["AWS_REGION"],
    }, 200 