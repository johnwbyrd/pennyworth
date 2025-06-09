from utils import tracer


@tracer.capture_method
def well_known_handler():
    import os

    return {
        "UserPoolId": os.environ["PENNYWORTH_USER_POOL_ID"],
        "UserPoolClientId": os.environ["PENNYWORTH_USER_POOL_CLIENT_ID"],
        "IdentityPoolId": os.environ["PENNYWORTH_IDENTITY_POOL_ID"],
        "Region": os.environ["PENNYWORTH_AWS_REGION"],
    }, 200
