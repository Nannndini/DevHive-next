import os
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET")

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


def _hash_password(password: str, rounds: int = 12) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds)).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _create_jwt(email: str, role: str, name: str) -> str:
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="Server misconfigured: JWT_SECRET is not set")
    now = datetime.now(timezone.utc)
    payload = {
        "email": email, "role": role, "name": name,
        "iat": now, "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# Demo accounts. Disable on any deployment you don't want shared logins on:
#   ENABLE_DEMO_USERS=false
DEMO_USERS_ENABLED = os.environ.get("ENABLE_DEMO_USERS", "true").lower() != "false"
SEED_USERS = {}
if DEMO_USERS_ENABLED:
    SEED_USERS = {
        "admin@devhive.ai": {"password_hash": _hash_password("admin123", 4), "role": "admin", "name": "Admin User"},
        "manager@devhive.ai": {"password_hash": _hash_password("man@123", 4), "role": "manager", "name": "Manager User"},
        "employee@devhive.ai": {"password_hash": _hash_password("emp@123", 4), "role": "employee", "name": "Employee User"},
    }


def _query_user_from_db(email: str):
    """Return a user dict or None. Raises if the database is unreachable."""
    from api.database import SessionLocal
    from api.models import User

    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            return None
        return {"password_hash": u.password_hash, "role": u.role, "name": u.name or ""}
    finally:
        db.close()


def _create_user_in_db(email: str, password_hash: str, role: str, name: str) -> None:
    from api.database import SessionLocal
    from api.models import User

    db = SessionLocal()
    try:
        db.add(User(email=email, password_hash=password_hash, role=role, name=name))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.post("/login")
async def login(request: LoginRequest):
    email = request.email.strip().lower()

    try:
        user = _query_user_from_db(email)
    except Exception:
        logger.exception("User lookup failed")
        if email in SEED_USERS:
            user = SEED_USERS[email]
        else:
            raise HTTPException(status_code=503, detail="Database unavailable. Please try again.")
    else:
        if user is None:
            user = SEED_USERS.get(email)

    if not user or not _verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "token": _create_jwt(email, user["role"], user["name"]),
        "user": {"email": email, "role": user["role"], "name": user["name"]},
    }


@router.post("/register")
async def register(request: RegisterRequest):
    email = request.email.strip().lower()
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if email in SEED_USERS:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        if _query_user_from_db(email) is not None:
            raise HTTPException(status_code=400, detail="Email already registered")
        _create_user_in_db(email, _hash_password(request.password), "employee", request.full_name)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Registration failed")
        raise HTTPException(status_code=503, detail="Could not create the account. Please try again.")

    return {
        "token": _create_jwt(email, "employee", request.full_name),
        "user": {"email": email, "role": "employee", "name": request.full_name},
    }
