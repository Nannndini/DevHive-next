import os
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required but not set.")

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


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_jwt(email: str, role: str, name: str) -> str:
    payload = {
        "email": email,
        "role": role,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _query_user_from_db(email: str):
    """Try to find user in the database User table. Returns dict or None."""
    try:
        from database import SessionLocal
        from models import User
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.email == email).first()
            if db_user:
                return {
                    "password_hash": db_user.password_hash,
                    "role": db_user.role,
                    "name": db_user.name or "",
                }
            return None
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"DB lookup failed, falling back to seed users: {e}")
        return None


def _create_user_in_db(email: str, password_hash: str, role: str, name: str) -> bool:
    """Try to insert a new user into the database. Returns True on success."""
    try:
        from database import SessionLocal
        from models import User
        db = SessionLocal()
        try:
            new_user = User(
                email=email,
                password_hash=password_hash,
                role=role,
                name=name,
            )
            db.add(new_user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"DB write failed: {e}")
        return False


# Seeded demo users with bcrypt-hashed passwords.
SEED_USERS = {
    "admin@devhive.ai": {
        "password_hash": _hash_password("admin123"),
        "role": "admin",
        "name": "Admin User",
    },
    "manager@devhive.ai": {
        "password_hash": _hash_password("man@123"),
        "role": "manager",
        "name": "Manager User",
    },
    "employee@devhive.ai": {
        "password_hash": _hash_password("emp@123"),
        "role": "employee",
        "name": "Employee User",
    },
}

_registered_users = {}


@router.post("/login")
async def login(request: LoginRequest):
    # 1. Try database User table first
    user = _query_user_from_db(request.email)

    # 2. Fall back to seed users, then runtime-registered users
    if user is None:
        user = SEED_USERS.get(request.email) or _registered_users.get(request.email)

    if not user or not _verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_jwt(request.email, user["role"], user["name"])

    return {
        "token": token,
        "user": {
            "email": request.email,
            "role": user["role"],
            "name": user["name"],
        },
    }


@router.post("/register")
async def register(request: RegisterRequest):
    if request.email in SEED_USERS or request.email in _registered_users:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = _query_user_from_db(request.email)
    if db_user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = _hash_password(request.password)

    _create_user_in_db(request.email, password_hash, "employee", request.full_name)

    _registered_users[request.email] = {
        "password_hash": password_hash,
        "role": "employee",
        "name": request.full_name,
    }

    token = _create_jwt(request.email, "employee", request.full_name)

    return {
        "token": token,
        "user": {
            "email": request.email,
            "role": "employee",
            "name": request.full_name,
        },
    }
