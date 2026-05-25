from __future__ import annotations

import pytest
from fastapi import HTTPException

from src.core.models import Role
from src.security.rbac import _decode_token, create_token


def test_create_and_decode_token() -> None:
    token = create_token("user1", Role.editor)
    payload = _decode_token(token)
    assert payload.sub == "user1"
    assert payload.role == Role.editor


def test_decode_invalid_token_raises_401() -> None:
    with pytest.raises(HTTPException) as exc_info:
        _decode_token("not.a.valid.token")
    assert exc_info.value.status_code == 401


def test_all_roles_roundtrip() -> None:
    for role in Role:
        token = create_token("tester", role)
        payload = _decode_token(token)
        assert payload.role == role
        assert payload.sub == "tester"


def test_token_has_expiry() -> None:
    token = create_token("u", Role.viewer)
    payload = _decode_token(token)
    assert payload.exp is not None
