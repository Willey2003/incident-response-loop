"""
Authentication routes for Target API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from uuid import uuid4

from ..config import settings
from ..kafka import get_producer

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    mfa_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class UserInfo(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []


class MFAChallengeResponse(BaseModel):
    challenge_id: str
    method: str
    expires_at: datetime


router = APIRouter()

# In-memory user store for demo
DEMO_USERS = {
    "admin": {
        "user_id": "user-001",
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S",  # "password123"
        "roles": ["administrator"],
        "permissions": ["*"],
    },
    "user1": {
        "user_id": "user-002",
        "username": "user1",
        "email": "user1@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S",  # "password123"
        "roles": ["user"],
        "permissions": ["read", "write"],
    },
    "service-account": {
        "user_id": "user-003",
        "username": "service-account",
        "email": "service@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S",
        "roles": ["service"],
        "permissions": ["api:read", "api:write"],
    },
}

# Simple password verification (in production, use bcrypt)
def verify_password(password: str, password_hash: str) -> bool:
    # In production, use bcrypt.checkpw
    # For demo, accept "password123" for all demo users
    return password == "password123"


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    from jose import jwt
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, "dev-secret", algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    from jose import jwt
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, "dev-secret", algorithm="HS256")


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token."""
    user = DEMO_USERS.get(request.username)
    
    if not user or not verify_password(request.password, user["password_hash"]):
        # Emit failed login event
        event = {
            "event_id": f"evt-{uuid4()}",
            "event_type": "login_failed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "target-api",
            "source_type": "api",
            "user_id": None,
            "username": request.username,
            "source_ip": "127.0.0.1",
            "user_agent": "demo-client",
            "success": False,
            "error_code": "AUTH_FAILED",
            "error_message": "Invalid credentials",
        }
        # Emit event to Kafka (simplified)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Successful login
    access_token = create_access_token(
        data={"sub": user["user_id"], "username": user["username"], "roles": user["roles"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["user_id"], "type": "refresh"}
    )
    
    # Emit success event
    event = {
        "event_id": f"evt-{uuid4()}",
        "event_type": "login_success",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "target-api",
        "source_type": "api",
        "user_id": user["user_id"],
        "username": request.username,
        "source_ip": "127.0.0.1",
        "user_agent": "demo-client",
        "success": True,
    }
    # Emit event to Kafka
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
    )


@router.post("/logout")
async def logout():
    """Logout user (invalidate token)."""
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Field(..., embed=True)):
    """Refresh access token."""
    # In production, validate refresh token
    new_access_token = create_access_token(data={"sub": "user-001", "username": "user1"})
    return TokenResponse(access_token=new_access_token, expires_in=3600)


@router.get("/me", response_model=UserInfo)
async def get_current_user():
    """Get current user info."""
    return UserInfo(
        user_id="user-001",
        username="admin",
        email="admin@example.com",
        roles=["administrator"],
        permissions=["*"],
    )


@router.post("/mfa/challenge", response_model=MFAChallengeResponse)
async def mfa_challenge(method: str = "totp"):
    """Initiate MFA challenge."""
    challenge_id = str(uuid4())
    return MFAChallengeResponse(
        challenge_id=challenge_id,
        method=method,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )


@router.post("/mfa/verify")
async def mfa_verify(challenge_id: str, code: str):
    """Verify MFA code."""
    # In production, verify TOTP code
    return {"verified": True, "message": "MFA verified successfully"}