"""
Users routes for Target API.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import uuid4

from ..config import settings

router = APIRouter()


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    roles: List[str] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
):
    """List users with filtering and pagination."""
    # Demo user data
    users = [
        {
            "user_id": "user-001",
            "username": "admin",
            "email": "admin@example.com",
            "roles": ["administrator"],
            "permissions": ["*"],
            "created_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-15T10:30:00Z",
            "is_active": True,
        },
        {
            "user_id": "user-002",
            "username": "user1",
            "email": "user1@example.com",
            "roles": ["user"],
            "permissions": ["read", "write"],
            "created_at": "2024-01-05T00:00:00Z",
            "last_login": "2024-01-14T15:20:00Z",
            "is_active": True,
        },
        {
            "user_id": "user-003",
            "username": "service-account",
            "email": "service@example.com",
            "roles": ["service"],
            "permissions": ["api:read", "api:write"],
            "created_at": "2024-01-10T00:00:00Z",
            "last_login": "2024-01-15T08:00:00Z",
            "is_active": True,
        },
    ]
    
    # Apply filters
    filtered_users = users
    if is_active is not None:
        filtered_users = [u for u in filtered_users if u["is_active"] == is_active]
    if role:
        filtered_users = [u for u in filtered_users if role in u["roles"]]
    
    # Pagination
    total = len(filtered_users)
    offset = (page - 1) * page_size
    paginated_users = filtered_users[offset:offset + page_size]
    
    return UserListResponse(
        users=[UserResponse(**u) for u in paginated_users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
    # Demo: return hardcoded user
    if user_id == "user-001":
        return UserResponse(
            user_id="user-001",
            username="admin",
            email="admin@example.com",
            roles=["administrator"],
            permissions=["*"],
            created_at=datetime(2024, 1, 1),
            last_login=datetime(2024, 1, 15, 10, 30),
            is_active=True,
        )
    
    raise HTTPException(status_code=404, detail="User not found")


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(request: UserCreateRequest):
    """Create a new user."""
    return UserResponse(
        user_id=str(uuid4()),
        username=request.username,
        email=request.email,
        roles=request.roles,
        permissions=["read", "write"],
        created_at=datetime.utcnow(),
        last_login=None,
        is_active=True,
    )


@router.patch("/{user_id}")
async def update_user(user_id: str, request: dict):
    """Update a user."""
    return {"message": "User updated", "user_id": user_id}


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user."""
    return {"message": "User deleted", "user_id": user_id}


@router.post("/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    """Deactivate a user."""
    return {"message": "User deactivated", "user_id": user_id}


@router.post("/{user_id}/activate")
async def activate_user(user_id: str):
    """Activate a user."""
    return {"message": "User activated", "user_id": user_id}


@router.post("/{user_id}/reset-password")
async def reset_password(user_id: str, new_password: str = Body(..., embed=True)):
    """Reset user password."""
    return {"message": "Password reset", "user_id": user_id}


@router.post("/{user_id}/mfa/enable")
async def enable_mfa(user_id: str, method: str = "totp"):
    """Enable MFA for user."""
    return {"message": "MFA enabled", "user_id": user_id, "method": method}


@router.post("/{user_id}/mfa/disable")
async def disable_mfa(user_id: str):
    """Disable MFA for user."""
    return {"message": "MFA disabled", "user_id": user_id}