from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import create_session, password_hash, require_admin, require_signed_in, token_digest, verify_password
from app.db import get_db
from app.models import LocalSession, LocalUser

router = APIRouter(prefix="/auth", tags=["Local Accounts"])


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=10, max_length=200)


class UserCreate(Credentials):
    role: str = Field(pattern="^(admin|staff)$")


def user_data(user: LocalUser) -> dict[str, object]:
    return {"id": user.id, "username": user.username, "role": user.role, "created_at": user.created_at}


def session_data(db: Session, user: LocalUser) -> dict[str, object]:
    return {"token": create_session(db, user), "user": user_data(user)}


@router.get("/status")
def account_status(db: Session = Depends(get_db)) -> dict[str, bool]:
    return {"setup_required": (db.scalar(select(func.count()).select_from(LocalUser)) or 0) == 0}


@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup_first_admin(payload: Credentials, db: Session = Depends(get_db)) -> dict[str, object]:
    if (db.scalar(select(func.count()).select_from(LocalUser)) or 0) != 0:
        raise HTTPException(status_code=409, detail="An administrator account has already been set up.")
    user = LocalUser(username=payload.username.strip(), password_hash=password_hash(payload.password), role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)
    return session_data(db, user)


@router.post("/login")
def login(payload: Credentials, db: Session = Depends(get_db)) -> dict[str, object]:
    user = db.scalar(select(LocalUser).where(func.lower(LocalUser.username) == payload.username.strip().lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect.")
    return session_data(db, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db), _: LocalUser = Depends(require_signed_in)) -> None:
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    db.query(LocalSession).filter(LocalSession.token_hash == token_digest(token)).delete()
    db.commit()


@router.get("/me")
def current_user(user: LocalUser = Depends(require_signed_in)) -> dict[str, object]:
    return user_data(user)


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: LocalUser = Depends(require_admin)) -> list[dict[str, object]]:
    return [user_data(user) for user in db.scalars(select(LocalUser).order_by(LocalUser.username)).all()]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: LocalUser = Depends(require_admin)) -> dict[str, object]:
    username = payload.username.strip()
    if db.scalar(select(LocalUser).where(func.lower(LocalUser.username) == username.lower())):
        raise HTTPException(status_code=409, detail="That username is already in use.")
    user = LocalUser(username=username, password_hash=password_hash(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user_data(user)
