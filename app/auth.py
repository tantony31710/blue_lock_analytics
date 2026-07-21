"""
JWT authentication for the dashboard/analytics endpoints.

Device telemetry ingestion does NOT use this — machines authenticate
with a shared API key instead (see app/device_auth.py). This module is
for humans logging into the dashboard.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.storage import StorageManager

# In production, set JWT_SECRET_KEY as a real environment variable —
# this fallback exists only so local dev works out of the box.
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-insecure-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# bcrypt has a hard 72-byte input limit — truncate rather than error,
# same behavior passlib's bcrypt backend uses.
_MAX_PASSWORD_BYTES = 72


def hash_password(plain_password: str) -> str:
    truncated = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
    return bcrypt.checkpw(truncated, hashed_password.encode("utf-8"))


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: StorageManager, username: str, password: str) -> Optional[dict]:
    user = db.get_user(username)
    if user is None or not verify_password(password, user["hashed_password"]):
        return None
    return user


def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """FastAPI dependency: decodes the bearer token, returns the username,
    or raises 401 if the token is missing/invalid/expired."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_error
        return username
    except JWTError:
        raise credentials_error
