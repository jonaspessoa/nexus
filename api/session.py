import hashlib
import os
import secrets
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

router = APIRouter(prefix="/session")
COOKIE = "nexus_session"
SESSION_SECONDS = 8 * 60 * 60


@lru_cache
def database():
    return create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Login(BaseModel):
    password: str = Field(max_length=256)


@router.post("", status_code=204)
def login(body: Login, response: Response):
    password = os.getenv("NEXUS_OPERATOR_PASSWORD", "")
    if len(password) < 16:
        raise HTTPException(503, "Operator password is not configured")
    if not secrets.compare_digest(body.password.encode(), password.encode()):
        raise HTTPException(401, "Invalid password")
    token = secrets.token_urlsafe(32)
    with database().begin() as connection:
        connection.execute(text("DELETE FROM operator_sessions WHERE expires_at <= now()"))
        connection.execute(
            text(
                "INSERT INTO operator_sessions (token_hash, expires_at) "
                "VALUES (:hash, now() + :seconds * interval '1 second')"
            ),
            {"hash": token_hash(token), "seconds": SESSION_SECONDS},
        )
    response.set_cookie(
        COOKIE, token, max_age=SESSION_SECONDS, httponly=True, samesite="strict",
        secure=os.getenv("NEXUS_SECURE_COOKIE") == "1",
    )


def require_operator(nexus_session: Annotated[str | None, Cookie()] = None):
    if not nexus_session:
        raise HTTPException(401, "Sign in required")
    with database().connect() as connection:
        active = connection.execute(
            text(
                "SELECT 1 FROM operator_sessions "
                "WHERE token_hash = :hash AND expires_at > now()"
            ),
            {"hash": token_hash(nexus_session)},
        ).scalar()
    if not active:
        raise HTTPException(401, "Sign in required")


@router.delete("", status_code=204)
def logout(response: Response, nexus_session: Annotated[str | None, Cookie()] = None):
    if nexus_session:
        with database().begin() as connection:
            connection.execute(
                text("DELETE FROM operator_sessions WHERE token_hash = :hash"),
                {"hash": token_hash(nexus_session)},
            )
    response.delete_cookie(COOKIE)
