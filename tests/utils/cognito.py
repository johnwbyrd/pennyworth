import boto3
from src.shared.constants import *

def get_cognito_client():
    region = PENNYWORTH_AWS_REGION
    return boto3.client('cognito-idp', region_name=region)

def create_user(username, email, password, group='user'):
    user_pool_id = PENNYWORTH_USER_POOL_ID
    client = get_cognito_client()
    # Create the user (suppress invite email)
    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {'Name': 'email', 'Value': email},
            {'Name': 'email_verified', 'Value': 'true'},
        ],
        TemporaryPassword=password,
        MessageAction='SUPPRESS',
    )
    # Set the password as permanent
    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=username,
        Password=password,
        Permanent=True
    )
    # Add to group
    client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=username,
        GroupName=group
    )

def delete_user(username):
    user_pool_id = PENNYWORTH_USER_POOL_ID
    client = get_cognito_client()
    client.admin_delete_user(
        UserPoolId=user_pool_id,
        Username=username
    ) 