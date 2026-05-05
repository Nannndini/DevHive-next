from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

# Mock user database
USERS = {
    "admin@devhive.ai": {"password": "password", "role": "admin", "name": "Admin User"},
    "manager@devhive.ai": {"password": "password", "role": "manager", "name": "Manager User"},
    "employee@devhive.ai": {"password": "password", "role": "employee", "name": "Employee User"},
}

@router.post("/login")
async def login(request: LoginRequest):
    user = USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # In a real app, generate a JWT. Here we return a mock token.
    token = f"mock-jwt-token-{user['role']}"
    
    return {
        "token": token,
        "user": {
            "email": request.email,
            "role": user["role"],
            "name": user["name"]
        }
    }
