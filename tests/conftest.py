"""Test configuration and fixtures for the Pennyworth test suite."""

import os
import pytest
import secrets
import uuid

from src.shared.session import get_session
from tests.utils.cognito import create_user, delete_user
from src.shared.constants import *

@pytest.fixture(scope='session')
def test_users():
    """Create test users in Cognito for testing.
    
    Creates both admin and regular user accounts with secure random credentials.
    Yields user details and cleans up after tests complete.
    """
    # Generate secure, random user details
    admin_username = f"admin_{uuid.uuid4().hex}"
    user_username = f"user_{uuid.uuid4().hex}"
    admin_email = f"{admin_username}@example.com"
    user_email = f"{user_username}@example.com"
    admin_password = secrets.token_urlsafe(16)
    user_password = secrets.token_urlsafe(16)

    # Create users in Cognito
    create_user(admin_username, admin_email, admin_password, group='admin')
    create_user(user_username, user_email, user_password, group='user')
    yield {
        'admin': {'username': admin_username, 'password': admin_password},
        'user': {'username': user_username, 'password': user_password}
    }
    # Cleanup
    delete_user(admin_username)
    delete_user(user_username)

@pytest.fixture(scope='session')
def jwt_tokens(test_users):
    """Generate JWT tokens for test users.
    
    Uses the test_users fixture to authenticate and get JWT tokens
    for both admin and regular users.
    """
    admin_session = get_session({'username': test_users['admin']['username'], 'password': test_users['admin']['password']})
    user_session = get_session({'username': test_users['user']['username'], 'password': test_users['user']['password']})
    return {
        'admin_jwt': admin_session['jwt_token'],
        'user_jwt': user_session['jwt_token']
    } 