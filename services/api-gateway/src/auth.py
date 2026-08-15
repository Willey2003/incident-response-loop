"""
Authentication and authorization for API Gateway.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from pydantic import BaseModel, Field

from .config import settings
from .database import get_db
from .redis import get_redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oidc_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/auth/realms/aegisforge/protocol/openid-connect/auth",
    tokenUrl="/auth/realms/aegisforge/protocol/openid-connect/token",
)


class TokenData(BaseModel):
    """JWT token payload."""
    sub: str
    username: str
    email: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    exp: int
    iat: int
    jti: str
    token_type: str = "access"


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class UserInDB(BaseModel):
    """User model from database."""
    id: UUID
    username: str
    email: str
    hashed_password: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class TokenBlacklist:
    """Manage token blacklist in Redis."""
    
    def __init__(self, redis_client):
        self.redis = redis
        self.prefix = "blacklist:"
    
    async def add(self, token: str, expires_in: int) -> None:
        """Add token to blacklist."""
        key = f"blacklist:{token}"
        await self.redis.setex(key, expires_in, "1")
    
    async def is_blacklisted(self, token: str) -> bool:
        return await self.redis.exists(f"blacklist:{token}") > 0
    
    async def remove(self, token: str) -> None:
        await self.redis.delete(f"blacklist:{token}")


# Password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT functions
def create_access_token(
    data: Dict[str, any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "token_type": token_type,
    })
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: Dict[str, any]) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRY_DAYS)
    to_encode = data.copy()
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "token_type": "refresh",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenData(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Token blacklist dependency
async def get_token_blacklist() -> TokenBlacklist:
    redis_client = get_redis()
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return TokenBlacklist(redis)


# OIDC configuration (Keycloak)
OIDC_CONFIG = {
    "issuer": settings.OIDC_ISSUER_URL,
    "client_id": settings.OIDC_CLIENT_ID,
    "client_secret": settings.OIDC_CLIENT_SECRET,
    "redirect_uri": settings.OIDC_REDIRECT_URI,
}


# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> UserInDB:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check blacklist
    blacklist = TokenBlacklist(redis_client)
    if await blacklist.is_blacklisted(token):
        raise credentials_exception
    
    # Decode token
    try:
        token_data = decode_token(token)
    except HTTPException:
        raise credentials_exception
    
    # Check token type
    if token_data.token_type != "access":
        raise credentials_exception
    
    # Check expiration
    if datetime.utcnow().timestamp() > token_data.exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    from sqlalchemy import select
    from uuid import UUID
    
    user_id = UUID(token_data.sub)
    result = await db.execute(select(UserInDB).where(UserInDB.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_roles: List[str]):
    """Dependency to require specific roles."""
    def role_checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker


def require_permission(required_permissions: List[str]):
    """Dependency to require specific permissions."""
    def permission_checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if not any(perm in current_user.permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return permission_checker


# Role-based dependencies
require_admin = require_role(["administrator"])
require_incident_commander = require_role(["incident_commander", "administrator"])
require_analyst = require_role(["analyst", "incident_commander", "administrator"])
require_viewer = require_role(["viewer", "analyst", "incident_commander", "administrator"])


# Permission-based dependencies
require_alert_manage = require_permission(["alert:manage"])
require_incident_manage = require_permission(["incident:manage"])
require_response_approve = require_permission(["response:approve"])
require_emulation_control = require_permission(["emulation:control"])
require_admin_access = require_permission(["admin:access"])