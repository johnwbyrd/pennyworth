# User and API key management handlers (stubs)

from errors import NotImplementedException

def create_user_handler(body):
    raise NotImplementedException("Not implemented: create_user")

def get_user_handler(user_id):
    raise NotImplementedException(f"Not implemented: get_user {user_id}")

def update_user_handler(user_id, body):
    raise NotImplementedException(f"Not implemented: update_user {user_id}")

def delete_user_handler(user_id):
    raise NotImplementedException(f"Not implemented: delete_user {user_id}")

def list_users_handler():
    raise NotImplementedException("Not implemented: list_users")

def create_or_rotate_apikey_handler(user_id):
    raise NotImplementedException(f"Not implemented: create_or_rotate_apikey {user_id}")

def revoke_apikey_handler(user_id):
    raise NotImplementedException(f"Not implemented: revoke_apikey {user_id}")

def get_apikey_status_handler(user_id):
    raise NotImplementedException(f"Not implemented: get_apikey_status {user_id}") 