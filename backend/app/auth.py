import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import LocalSession, LocalUser

SESSION_HOURS = 12
PASSWORD_ITERATIONS = 310_000


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_text, digest_text = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), base64.b64decode(salt_text), int(iterations)
        )
        return hmac.compare_digest(candidate, base64.b64decode(digest_text))
    except (TypeError, ValueError):
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: Session, user: LocalUser) -> str:
    db.execute(delete(LocalSession).where(LocalSession.expires_at <= utc_now()))
    token = secrets.token_urlsafe(32)
    db.add(LocalSession(
        user_id=user.id,
        token_hash=token_digest(token),
        expires_at=utc_now() + timedelta(hours=SESSION_HOURS),
    ))
    db.commit()
    return token


def require_signed_in(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> LocalUser:
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in to continue.")
    session = db.scalar(
        select(LocalSession).where(
            LocalSession.token_hash == token_digest(token),
            LocalSession.expires_at > utc_now(),
        )
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your sign-in has expired. Please sign in again.")
    user = db.get(LocalUser, session.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in to continue.")
    return user


def require_admin(user: LocalUser = Depends(require_signed_in)) -> LocalUser:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access is required for this action.")
    return user
