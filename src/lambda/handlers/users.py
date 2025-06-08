# User and API key management handlers (stubs)

from errors import NotImplementedException
from auth import get_user_boto3_session
from errors import ForbiddenException, BadRequestException
import os

def create_user_handler(event, body):
    """
    Creates a new Cognito user using the permissions of the calling user (via Cognito Identity Pool).
    Expects body to contain: username, email, password, and (optionally) group.
    Returns the new user's username and status on success.
    """
    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if not body.get(field):
            raise BadRequestException(f"Missing required field: {field}")
    username = body["username"]
    email = body["email"]
    password = body["password"]
    group = body.get("group") or "user"

    session = get_user_boto3_session(event)
    cognito = session.client("cognito-idp")
    user_pool_id = os.environ["USER_POOL_ID"]

    try:
        # Create the user
        resp = cognito.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            TemporaryPassword=password,
            MessageAction="SUPPRESS",  # Don't send invite email
        )
        # Set the password as permanent
        cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=password,
            Permanent=True
        )
        # Always add to group (group is always set)
        cognito.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=username,
            GroupName=group
        )
        return {"username": username, "status": "CREATED"}, 201
    except cognito.exceptions.UsernameExistsException:
        raise BadRequestException(f"User '{username}' already exists.")
    except Exception as e:
        # If the user lacks permission, this will be a ForbiddenException
        raise ForbiddenException(str(e))

def get_user_handler(event, user_id):
    raise NotImplementedException(f"Not implemented: get_user {user_id}")

def update_user_handler(event, user_id, body):
    raise NotImplementedException(f"Not implemented: update_user {user_id}")

def delete_user_handler(event, user_id):
    raise NotImplementedException(f"Not implemented: delete_user {user_id}")

def list_users_handler(event):
    raise NotImplementedException("Not implemented: list_users")

def create_or_rotate_apikey_handler(event, user_id):
    raise NotImplementedException(f"Not implemented: create_or_rotate_apikey {user_id}")

def revoke_apikey_handler(event, user_id):
    raise NotImplementedException(f"Not implemented: revoke_apikey {user_id}")

def get_apikey_status_handler(event, user_id):
    raise NotImplementedException(f"Not implemented: get_apikey_status {user_id}") 