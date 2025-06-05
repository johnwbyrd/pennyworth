import os
import json

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "UserPoolId": os.environ["USER_POOL_ID"],
            "UserPoolClientId": os.environ["USER_POOL_CLIENT_ID"],
            "IdentityPoolId": os.environ["IDENTITY_POOL_ID"],
            "region": os.environ["AWS_REGION"]
        })
    } 