import pytest
import requests
import uuid
import secrets
from src.shared.constants import *

API_URL = PENNYWORTH_API_URL

@pytest.fixture
def random_user():
    """Generate a random test user with secure credentials."""
    username = f"test_{uuid.uuid4().hex}"
    email = f"{username}@example.com"
    password = secrets.token_urlsafe(16)
    return {"username": username, "email": email, "password": password}

@pytest.fixture
def no_auth_headers():
    """Return empty headers for unauthenticated requests."""
    return {}

@pytest.fixture
def user_auth_headers(jwt_tokens):
    """Return headers with regular user JWT token."""
    return {"Authorization": f"Bearer {jwt_tokens['user_jwt']}"}

@pytest.fixture
def admin_auth_headers(jwt_tokens):
    """Return headers with admin user JWT token."""
    return {"Authorization": f"Bearer {jwt_tokens['admin_jwt']}"}

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.users
def test_create_user_no_auth(random_user, no_auth_headers):
    """Test user creation without authentication fails."""
    resp = requests.post(f"{API_URL}/users", json=random_user, headers=no_auth_headers)
    assert resp.status_code in (401, 403)

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.users
def test_create_user_user_auth(random_user, user_auth_headers):
    """Test user creation with regular user auth fails."""
    resp = requests.post(f"{API_URL}/users", json=random_user, headers=user_auth_headers)
    assert resp.status_code in (401, 403)

@pytest.mark.integration
@pytest.mark.api
@pytest.mark.users
def test_create_user_admin_auth(random_user, admin_auth_headers):
    """Test user creation with admin auth succeeds."""
    resp = requests.post(f"{API_URL}/users", json=random_user, headers=admin_auth_headers)
    assert resp.status_code == 201 