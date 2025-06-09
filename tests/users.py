import pytest
import requests
import uuid
import secrets
from src.shared.constants import *

API_URL = PENNYWORTH_API_URL

@pytest.fixture
def random_user():
    username = f"test_{uuid.uuid4().hex}"
    email = f"{username}@example.com"
    password = secrets.token_urlsafe(16)
    return {"username": username, "email": email, "password": password}

@pytest.fixture
def no_auth_headers():
    return {}

@pytest.fixture
def user_auth_headers(jwt_tokens):
    return {"Authorization": f"Bearer {jwt_tokens['user_jwt']}"}

@pytest.fixture
def admin_auth_headers(jwt_tokens):
    return {"Authorization": f"Bearer {jwt_tokens['admin_jwt']}"}

@pytest.mark.user
def test_create_user_no_auth(random_user, no_auth_headers):
    resp = requests.post(f"{API_URL}/users", json=random_user, headers=no_auth_headers)
    assert resp.status_code in (401, 403)

@pytest.mark.user
def test_create_user_user_auth(random_user, user_auth_headers):
    resp = requests.post(f"{API_URL}/users", json=random_user, headers=user_auth_headers)
    assert resp.status_code in (401, 403)

@pytest.mark.user
def test_create_user_admin_auth(random_user, admin_auth_headers):
    resp = requests.post(f"{API_URL}/users", json=random_user, headers=admin_auth_headers)
    assert resp.status_code == 201 