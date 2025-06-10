import pytest
import requests
from src.shared.constants import *

API_URL = PENNYWORTH_API_URL

@pytest.mark.unit
@pytest.mark.handlers
@pytest.mark.parameters
def test_well_known_endpoint():
    """Test that the well-known endpoint returns the expected Cognito configuration."""
    resp = requests.get(f"{API_URL}/parameters/well-known")
    assert resp.status_code == 200
    
    data = resp.json()
    assert data["UserPoolId"]
    assert data["UserPoolClientId"]
    assert data["IdentityPoolId"]
    assert data["Region"] 