from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from src.core.config import settings
from src.core.models import Role

_bearer = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    sub: str
    role: Role
    exp: datetime


def create_token(subject: str, role: Role) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "role": role.value, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> TokenPayload:
    try:
        data = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return TokenPayload(sub=data["sub"], role=Role(data["role"]), exp=data["exp"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> TokenPayload:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return _decode_token(credentials.credentials)


def require_role(*roles: Role):  # type: ignore[no-untyped-def]
    def dependency(user: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} not allowed. Required: {[r.value for r in roles]}",
            )
        return user

    return dependency
