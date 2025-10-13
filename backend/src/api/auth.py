from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Simple user store (in production, use a proper database)
USERS = {
    "admin@ecu.edu.au": {"password": "admin123", "role": "admin", "name": "Administrator"},
    "flavio@ecu.edu.au": {"password": "flavio123", "role": "faculty", "name": "Flavio"}
}

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

def create_token(email: str) -> str:
    """Create JWT token"""
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        email = payload.get("email")
        if email not in USERS:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Login endpoint"""
    user = USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(request.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={"email": request.email, "name": user["name"], "role": user["role"]}
    )

@router.get("/me")
def get_current_user(email: str = Depends(verify_token)):
    """Get current user info"""
    user = USERS[email]
    return {"email": email, "name": user["name"], "role": user["role"]}