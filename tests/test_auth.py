# tests/test_auth.py
import pytest
from app.core.security import create_access_token, decode_access_token

def test_token_encode_decode():
    token = create_access_token(subject="EMPTEST", roles=["manager"])
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == "EMPTEST"
    assert "roles" in payload and "manager" in payload["roles"]
