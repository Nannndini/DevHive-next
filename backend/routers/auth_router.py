from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

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

@router.post("/register")
async def register(request: RegisterRequest):
    if request.email in USERS:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Add to mock database
    USERS[request.email] = {
        "password": request.password,
        "role": "employee", # Default role
        "name": request.full_name
    }
    
    token = "mock-jwt-token-employee"
    
    return {
        "token": token,
        "user": {
            "email": request.email,
            "role": "employee",
            "name": request.full_name
        }
    }
