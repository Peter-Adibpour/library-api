import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth import get_current_role, require_admin
from app.config import settings


def test_get_current_role_admin_token():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=settings.admin_token)
    assert get_current_role(creds) == "admin"


def test_get_current_role_member_token():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=settings.member_token)
    assert get_current_role(creds) == "member"


def test_get_current_role_unknown_token_raises_401_with_bearer_challenge():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-token")
    with pytest.raises(HTTPException) as exc_info:
        get_current_role(creds)
    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


def test_require_admin_allows_admin():
    assert require_admin("admin") == "admin"


def test_require_admin_rejects_member_with_403():
    with pytest.raises(HTTPException) as exc_info:
        require_admin("member")
    assert exc_info.value.status_code == 403